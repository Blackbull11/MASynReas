from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


L1_FAMILIES = ("structural", "dynamic", "functional", "procedural")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def maybe_load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return load_json(path)


def canonical_level1_agent_name(name: str) -> str:
    cleaned = (name or "").strip()
    if cleaned.endswith("_detector"):
        return cleaned[:-9]
    return cleaned


def normalize_records(payload: Any) -> List[Dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if payload.get("activation_status") == "not_triggered":
            return []
        for key in ("results", "bindings", "diagnoses", "items", "data", "records"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [payload]
    return []


def agent_name_from_result_file(path: Path) -> str:
    stem = path.stem
    if stem.endswith("_results"):
        return stem[:-8]
    return stem


def load_dataset_expectations(datasets_root: Path, dataset_id: str) -> Dict[str, Any]:
    dataset_dir = datasets_root / dataset_id
    return {
        "manifest": load_json(dataset_dir / "manifest.json"),
        "expected_level1": load_json(dataset_dir / "expected_level1.json"),
        "expected_level2": load_json(dataset_dir / "expected_level2.json"),
        "dataset_dir": dataset_dir,
    }


def load_run_context(results_root: Path) -> Dict[str, Any]:
    context = maybe_load_json(results_root / "metrics" / "run_context.json")
    return context or {}


def load_runtime_events(results_root: Path) -> List[Dict[str, Any]]:
    path = results_root / "metrics" / "runtime_events.jsonl"
    if not path.exists():
        return []

    events: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                events.append(parsed)
    return events


def load_actual_level1(results_root: Path, mode: str) -> Dict[str, Dict[str, Any]]:
    inventory: Dict[str, Dict[str, Any]] = {}
    for family in L1_FAMILIES:
        family_dir = results_root / family / mode
        if not family_dir.exists():
            continue
        for path in sorted(family_dir.glob("*.json")):
            payload = maybe_load_json(path)
            records = normalize_records(payload)
            agent = canonical_level1_agent_name(agent_name_from_result_file(path))
            inventory[agent] = {
                "family": family,
                "path": path,
                "payload": payload,
                "records": records,
                "count": len(records),
            }
    return inventory


def load_actual_level2(results_root: Path, mode: str) -> Dict[str, Dict[str, Any]]:
    inventory: Dict[str, Dict[str, Any]] = {}
    level2_dir = results_root / "level2" / mode
    if not level2_dir.exists():
        return inventory

    for path in sorted(level2_dir.glob("*.json")):
        payload = maybe_load_json(path) or {}
        diagnoses = payload.get("diagnoses", []) if isinstance(payload, dict) else []
        diagnoses = [item for item in diagnoses if isinstance(item, dict)]
        agent = agent_name_from_result_file(path)
        inventory[agent] = {
            "path": path,
            "payload": payload,
            "diagnoses": diagnoses,
            "count": len(diagnoses),
            "activation_status": payload.get("activation_status", "missing") if isinstance(payload, dict) else "missing",
            "reason": payload.get("reason") if isinstance(payload, dict) else None,
        }
    return inventory


def flatten_actual_diagnoses(level2_inventory: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    flat: List[Dict[str, Any]] = []
    for agent, entry in level2_inventory.items():
        for diagnosis in entry["diagnoses"]:
            enriched = dict(diagnosis)
            enriched["agent"] = agent
            flat.append(enriched)
    flat.sort(
        key=lambda item: (
            -int(item.get("priority_score", 0)),
            -int(item.get("severity_score", 0)),
            -int(item.get("reliability_score", 0)),
            str(item.get("target_id", "")),
            str(item.get("agent", "")),
        )
    )
    return flat


def expected_l1_counts(expected_level1: Dict[str, Any], mode: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    mode_payload = expected_level1.get(mode, {})
    for family in L1_FAMILIES:
        family_payload = mode_payload.get(family, {})
        for agent, items in family_payload.items():
            counts[canonical_level1_agent_name(agent)] = len(items)
    return counts


def expected_l2_entries(expected_level2: Dict[str, Any], mode: str) -> Dict[str, List[Dict[str, Any]]]:
    mode_payload = expected_level2.get(mode, {})
    return {agent: list(items) for agent, items in mode_payload.items()}


def expected_l2_keys(expected_level2: Dict[str, Any], mode: str) -> List[Tuple[str, str]]:
    entries = []
    for agent, items in expected_l2_entries(expected_level2, mode).items():
        for item in items:
            anchor = str(item.get("anchor", ""))
            if anchor:
                entries.append((agent, anchor))
    return entries


def actual_l2_keys(flat_actual_diagnoses: Iterable[Dict[str, Any]]) -> List[Tuple[str, str]]:
    entries: List[Tuple[str, str]] = []
    for item in flat_actual_diagnoses:
        agent = str(item.get("agent", ""))
        target = str(item.get("target_id", ""))
        if agent and target:
            entries.append((agent, target))
    return entries


def safe_ratio(numerator: int, denominator: int) -> Optional[float]:
    if denominator == 0:
        return None
    return numerator / denominator


def metric_record(
    *,
    metric_name: str,
    scope: str,
    dataset_id: str,
    mode: str,
    value: Optional[float],
    unit: str,
    counts: Optional[Dict[str, Any]] = None,
    breakdown: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "metric_name": metric_name,
        "scope": scope,
        "dataset_id": dataset_id,
        "mode": mode,
        "value": value,
        "unit": unit,
    }
    if counts is not None:
        payload["counts"] = counts
    if breakdown is not None:
        payload["breakdown"] = breakdown
    if parameters is not None:
        payload["parameters"] = parameters
    return payload
