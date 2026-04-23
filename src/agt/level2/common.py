from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class AnchorRule:
    anchor_type: str
    keys: Tuple[str, ...]
    multi: bool = False


@dataclass(frozen=True)
class InputSpec:
    agent: str
    family: str
    mode: str
    result_stem: str
    role: str
    label: str
    anchor_rules: Tuple[AnchorRule, ...]
    severity_tags: Tuple[str, ...] = ()

    @property
    def relative_path(self) -> Path:
        return Path("results") / self.family / self.mode / f"{self.result_stem}.json"


CRITICALITY_KEYS = (
    "criticality",
    "businessCriticality",
    "business_criticality",
    "severity",
    "priority",
)


def binding_value(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, dict):
        return binding_value(value.get("value"))
    if isinstance(value, list):
        values = [binding_value(item) for item in value]
        cleaned = [item for item in values if item]
        return cleaned[0] if cleaned else None
    text = str(value).strip()
    return text if text else None


def all_binding_values(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        output: List[str] = []
        for item in value:
            output.extend(all_binding_values(item))
        return output
    extracted = binding_value(value)
    return [extracted] if extracted else []


def short_name(identifier: str) -> str:
    return identifier.rstrip("/").split("/")[-1]


def safe_load_json(path: Path) -> Tuple[bool, Any]:
    if not path.exists():
        return False, None

    try:
        with path.open("r", encoding="utf-8") as handle:
            return True, json.load(handle)
    except Exception:
        return True, None


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


def load_level1_inputs(
    project_root: Path,
    input_specs: Sequence[InputSpec],
) -> Dict[str, Dict[str, Any]]:
    loaded: Dict[str, Dict[str, Any]] = {}
    for spec in input_specs:
        exists, payload = safe_load_json(project_root / spec.relative_path)
        records = normalize_records(payload) if exists else []
        loaded[spec.agent] = {
            "spec": spec,
            "records": records,
            "exists": exists,
            "path": project_root / spec.relative_path,
        }
        state = "missing" if not exists else f"{len(records)} record(s)"
        print(f"[Level2] Loaded {spec.agent}: {state} from {spec.relative_path.as_posix()}")
    return loaded


def extract_first(record: Dict[str, Any], keys: Iterable[str]) -> Optional[str]:
    for key in keys:
        if key in record:
            value = binding_value(record.get(key))
            if value:
                return value
    return None


def extract_many(record: Dict[str, Any], keys: Iterable[str]) -> List[str]:
    values: List[str] = []
    for key in keys:
        if key in record:
            values.extend(all_binding_values(record.get(key)))
    deduped: List[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def extract_anchors(record: Dict[str, Any], rules: Sequence[AnchorRule]) -> Set[Tuple[str, str]]:
    anchors: Set[Tuple[str, str]] = set()
    for rule in rules:
        values = extract_many(record, rule.keys) if rule.multi else []
        if not rule.multi:
            first = extract_first(record, rule.keys)
            if first:
                values = [first]
        for value in values:
            anchors.add((rule.anchor_type, value))
    return anchors


def collect_criticalities(record: Dict[str, Any]) -> Set[str]:
    criticalities: Set[str] = set()
    for key in CRITICALITY_KEYS:
        if key in record:
            value = binding_value(record.get(key))
            if value:
                criticalities.add(value.lower())
    return criticalities


def build_anchor_index(
    loaded: Dict[str, Dict[str, Any]],
) -> Dict[Tuple[str, str], Dict[str, Any]]:
    index: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for agent_name, payload in loaded.items():
        spec: InputSpec = payload["spec"]
        for record in payload["records"]:
            anchors = extract_anchors(record, spec.anchor_rules)
            for anchor_type, anchor_id in anchors:
                key = (anchor_type, anchor_id)
                if key not in index:
                    index[key] = {
                        "anchor_type": anchor_type,
                        "anchor_id": anchor_id,
                        "evidence": defaultdict(list),
                        "criticalities": set(),
                    }
                index[key]["evidence"][agent_name].append(record)
                index[key]["criticalities"].update(collect_criticalities(record))
    return index


def summarize_candidate(
    candidate: Dict[str, Any],
    input_specs: Dict[str, InputSpec],
) -> Dict[str, Any]:
    present_agents = set(candidate["evidence"].keys())
    primary_agents = {agent for agent in present_agents if input_specs[agent].role == "primary"}
    supporting_agents = {agent for agent in present_agents if input_specs[agent].role == "supporting"}
    contextual_agents = {agent for agent in present_agents if input_specs[agent].role == "contextual"}
    families = {input_specs[agent].family for agent in present_agents}
    total_records = sum(len(records) for records in candidate["evidence"].values())

    return {
        "present_agents": present_agents,
        "primary_agents": primary_agents,
        "supporting_agents": supporting_agents,
        "contextual_agents": contextual_agents,
        "families": families,
        "total_records": total_records,
        "criticalities": set(candidate["criticalities"]),
    }


def compute_reliability(summary: Dict[str, Any], anchor_type: str) -> int:
    primary_score = len(summary["primary_agents"]) * 20
    supporting_score = len(summary["supporting_agents"]) * 10
    family_count = len(summary["families"])
    if family_count >= 3:
        cross_family_bonus = 20
    elif family_count >= 2:
        cross_family_bonus = 10
    else:
        cross_family_bonus = 0

    if anchor_type in {"Resource", "Application", "Service", "ChangeRequest", "TroubleTicket", "Location"}:
        anchor_bonus = 15
    else:
        anchor_bonus = 5

    reliability_raw = primary_score + supporting_score + cross_family_bonus + anchor_bonus
    return max(0, min(100, reliability_raw))


def compute_severity(
    summary: Dict[str, Any],
    input_specs: Dict[str, InputSpec],
    base_bonus: int,
) -> Tuple[int, Dict[str, int]]:
    criticalities = summary["criticalities"]
    if {"critical", "high-critical", "high"} & criticalities:
        criticality_component = 20
    elif criticalities:
        criticality_component = 10
    else:
        criticality_component = 0

    total_records = summary["total_records"]
    if total_records >= 8:
        breadth_component = 15
    elif total_records >= 5:
        breadth_component = 12
    elif total_records >= 3:
        breadth_component = 8
    elif total_records >= 2:
        breadth_component = 5
    else:
        breadth_component = 0

    concentration_count = sum(
        1 for agent in summary["present_agents"] if "concentration" in input_specs[agent].severity_tags
    )
    concentration_component = min(20, concentration_count * 6 + (4 if len(summary["primary_agents"]) >= 3 else 0))

    temporal_count = sum(
        1 for agent in summary["present_agents"] if "temporal" in input_specs[agent].severity_tags
    )
    temporal_component = min(20, temporal_count * 6)

    governance_count = sum(
        1 for agent in summary["present_agents"] if "governance" in input_specs[agent].severity_tags
    )
    governance_component = min(15, governance_count * 5)

    severity_raw = (
        criticality_component
        + breadth_component
        + concentration_component
        + temporal_component
        + governance_component
        + base_bonus
    )
    severity_score = max(0, min(100, severity_raw))

    return severity_score, {
        "criticality": criticality_component,
        "breadth": breadth_component,
        "concentration": concentration_component,
        "temporal_aggravation": temporal_component,
        "governance_weakness": governance_component,
        "family_base_bonus": base_bonus,
    }


def compute_priority(reliability_score: int, severity_score: int) -> int:
    return round(0.55 * reliability_score + 0.45 * severity_score)


def build_evidence_entries(
    candidate: Dict[str, Any],
    input_specs: Dict[str, InputSpec],
) -> List[Dict[str, Any]]:
    evidence_entries: List[Dict[str, Any]] = []
    anchor_id = candidate["anchor_id"]
    for agent_name in sorted(candidate["evidence"].keys()):
        spec = input_specs[agent_name]
        evidence_entries.append(
            {
                "level1_agent": agent_name,
                "role": spec.role,
                "matched_anchor": anchor_id,
                "record_count": len(candidate["evidence"][agent_name]),
                "family": spec.family,
                "result_file": spec.relative_path.as_posix(),
            }
        )
    return evidence_entries


def build_generic_explanation(
    diagnosis_label: str,
    candidate: Dict[str, Any],
    summary: Dict[str, Any],
    input_specs: Dict[str, InputSpec],
) -> str:
    fragments = [input_specs[agent].label for agent in sorted(summary["present_agents"])]
    anchor_type = candidate["anchor_type"]
    anchor_name = short_name(candidate["anchor_id"])
    families = ", ".join(sorted(summary["families"]))
    joined = "; ".join(fragments)
    return (
        f"{diagnosis_label} is diagnosed for {anchor_type} '{anchor_name}' because "
        f"{joined} converge on the same anchor. The evidence spans {families} signal family/families."
    )


def export_results(
    output_path: Path,
    agent_name: str,
    mode: str,
    activation_status: str,
    reason: str,
    diagnoses: List[Dict[str, Any]],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "agent": agent_name,
        "mode": mode,
        "activation_status": activation_status,
        "reason": reason,
        "diagnoses": diagnoses,
    }
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def run_anchor_diagnoser(
    *,
    project_root: Path,
    output_path: Path,
    agent_name: str,
    mode: str,
    diagnosis_type: str,
    diagnosis_prefix: str,
    diagnosis_label: str,
    recommended_action: str,
    input_specs: Sequence[InputSpec],
    activation_predicate: Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Dict[str, Any]]], bool],
    candidate_predicate: Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Dict[str, Any]]], bool],
    reason_not_triggered: str,
    reason_no_candidate: str,
    base_bonus: int = 8,
    explanation_builder: Optional[
        Callable[[Dict[str, Any], Dict[str, Any], Dict[str, InputSpec]], str]
    ] = None,
) -> None:
    loaded = load_level1_inputs(project_root, input_specs)
    input_by_agent = {spec.agent: spec for spec in input_specs}
    anchor_index = build_anchor_index(loaded)

    triggered = False
    trigger_reason = reason_not_triggered
    for candidate in anchor_index.values():
        summary = summarize_candidate(candidate, input_by_agent)
        if activation_predicate(candidate, summary, loaded):
            triggered = True
            trigger_reason = (
                f"Activation conditions satisfied around {candidate['anchor_type']} "
                f"'{short_name(candidate['anchor_id'])}'."
            )
            break

    if not triggered:
        export_results(output_path, agent_name, mode, "not_triggered", trigger_reason, [])
        return

    diagnoses: List[Dict[str, Any]] = []
    counter = 1
    for candidate in anchor_index.values():
        summary = summarize_candidate(candidate, input_by_agent)
        if not candidate_predicate(candidate, summary, loaded):
            continue

        reliability_score = compute_reliability(summary, candidate["anchor_type"])
        severity_score, severity_factors = compute_severity(summary, input_by_agent, base_bonus)
        priority_score = compute_priority(reliability_score, severity_score)
        explanation = (
            explanation_builder(candidate, summary, input_by_agent)
            if explanation_builder
            else build_generic_explanation(diagnosis_label, candidate, summary, input_by_agent)
        )

        diagnoses.append(
            {
                "diagnosis_id": f"{diagnosis_prefix}-{counter:03d}",
                "diagnosis_type": diagnosis_type,
                "mode": mode,
                "target_type": candidate["anchor_type"],
                "target_id": candidate["anchor_id"],
                "activation_status": "triggered",
                "reliability_score": reliability_score,
                "severity_score": severity_score,
                "priority_score": priority_score,
                "evidence": build_evidence_entries(candidate, input_by_agent),
                "severity_factors": severity_factors,
                "criticalities": sorted(candidate["criticalities"]),
                "explanation": explanation,
                "recommended_action": recommended_action,
            }
        )
        counter += 1

    if not diagnoses:
        export_results(output_path, agent_name, mode, "triggered", reason_no_candidate, [])
        return

    diagnoses.sort(
        key=lambda item: (
            -item["priority_score"],
            -item["severity_score"],
            -item["reliability_score"],
            item["target_id"],
        )
    )
    export_results(output_path, agent_name, mode, "triggered", trigger_reason, diagnoses)
