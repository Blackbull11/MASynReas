from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple

from kpi_common import (
    actual_l2_keys,
    expected_l1_counts,
    expected_l2_entries,
    expected_l2_keys,
    flatten_actual_diagnoses,
    load_actual_level1,
    load_actual_level2,
    load_dataset_expectations,
    load_run_context,
    load_runtime_events,
    metric_record,
    safe_ratio,
)


RELEVANT_METRICS = [
    "l2_activation_correctness",
    "precision_l2",
    "top1_accuracy",
    "ranking_mrr",
    "end_to_end_runtime",
    "mean_runtime_l1",
    "mean_runtime_l2",
    "controller_waiting_overhead",
    "traceability_rate",
    "evidence_completeness_ratio",
    "mean_evidence_count",
    "structured_evidence_ratio",
]

HELPER_METRICS = [
    "l1_expectation_match_rate",
    "diagnosis_hit",
    "clean_control_success",
]


def infer_dataset_and_mode(results_root: Path, dataset_id: Optional[str], mode: Optional[str]) -> Tuple[str, str, Dict[str, Any]]:
    context = load_run_context(results_root)
    inferred_dataset = dataset_id or context.get("dataset_id") or "unspecified"
    inferred_mode = mode or context.get("mode") or "apriori"
    return inferred_dataset, inferred_mode, context


def compute_l1_expectation_match(expected_counts: Dict[str, int], actual_level1: Dict[str, Dict[str, Any]]) -> Tuple[Optional[float], Dict[str, Any]]:
    decisions = 0
    correct = 0
    breakdown: Dict[str, Any] = {}

    agent_names = sorted(set(expected_counts) | set(actual_level1))
    for agent in agent_names:
        expected_positive = expected_counts.get(agent, 0) > 0
        actual_positive = actual_level1.get(agent, {}).get("count", 0) > 0
        decisions += 1
        if expected_positive == actual_positive:
            correct += 1
        breakdown[agent] = {
            "expected_count": expected_counts.get(agent, 0),
            "actual_count": actual_level1.get(agent, {}).get("count", 0),
            "decision_correct": expected_positive == actual_positive,
        }

    return safe_ratio(correct, decisions), {
        "correct": correct,
        "total": decisions,
        "per_agent": breakdown,
    }


def compute_l2_activation(expected_entries: Dict[str, List[Dict[str, Any]]], actual_level2: Dict[str, Dict[str, Any]]) -> Tuple[Optional[float], Dict[str, Any]]:
    decisions = 0
    correct = 0
    breakdown: Dict[str, Any] = {}

    agent_names = sorted(set(expected_entries) | set(actual_level2))
    for agent in agent_names:
        expected_active = len(expected_entries.get(agent, [])) > 0
        actual_payload = actual_level2.get(agent, {})
        actual_active = False
        if actual_payload:
            actual_active = actual_payload.get("activation_status") != "not_triggered" or actual_payload.get("count", 0) > 0

        decisions += 1
        if expected_active == actual_active:
            correct += 1

        breakdown[agent] = {
            "expected_active": expected_active,
            "actual_active": actual_active,
            "diagnosis_count": actual_payload.get("count", 0),
            "activation_status": actual_payload.get("activation_status", "missing"),
            "decision_correct": expected_active == actual_active,
        }

    return safe_ratio(correct, decisions), {
        "correct": correct,
        "total": decisions,
        "per_agent": breakdown,
    }


def compute_l2_matching(expected_keys: List[Tuple[str, str]], actual_keys: List[Tuple[str, str]]) -> Dict[str, Any]:
    expected_set = set(expected_keys)
    actual_set = set(actual_keys)
    tp = sorted(expected_set & actual_set)
    fp = sorted(actual_set - expected_set)
    missed = sorted(expected_set - actual_set)
    return {
        "tp": tp,
        "fp": fp,
        "missed": missed,
        "tp_count": len(tp),
        "fp_count": len(fp),
        "missed_count": len(missed),
        "expected_count": len(expected_set),
        "actual_count": len(actual_set),
    }


def compute_top1(flat_actual_diagnoses: List[Dict[str, Any]], expected_key_set: set[Tuple[str, str]]) -> Optional[float]:
    if not expected_key_set:
        return None
    if not flat_actual_diagnoses:
        return 0.0
    top = flat_actual_diagnoses[0]
    return 1.0 if (top.get("agent"), top.get("target_id")) in expected_key_set else 0.0


def compute_mrr(flat_actual_diagnoses: List[Dict[str, Any]], expected_key_set: set[Tuple[str, str]]) -> Optional[float]:
    if not expected_key_set:
        return None
    for index, diagnosis in enumerate(flat_actual_diagnoses, start=1):
        key = (diagnosis.get("agent"), diagnosis.get("target_id"))
        if key in expected_key_set:
            return 1.0 / index
    return 0.0


def compute_traceability(flat_actual_diagnoses: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    if not flat_actual_diagnoses:
        return {
            "traceability_rate": None,
            "evidence_completeness_ratio": None,
            "mean_evidence_count": None,
            "structured_evidence_ratio": None,
            "counts": {"diagnoses": 0},
        }

    traceable = 0
    evidence_complete = 0
    structured = 0
    evidence_counts: List[int] = []

    for diagnosis in flat_actual_diagnoses:
        evidence = diagnosis.get("evidence", [])
        if isinstance(evidence, list) and evidence:
            evidence_complete += 1
        count = len(evidence) if isinstance(evidence, list) else 0
        evidence_counts.append(count)
        if diagnosis.get("diagnosis_id") and diagnosis.get("target_id") and isinstance(evidence, list) and evidence:
            traceable += 1

        structured_ok = isinstance(evidence, list) and bool(evidence)
        if structured_ok:
            for entry in evidence:
                if not isinstance(entry, dict):
                    structured_ok = False
                    break
                for key in ("level1_agent", "role", "matched_anchor", "record_count"):
                    if key not in entry:
                        structured_ok = False
                        break
        if structured_ok:
            structured += 1

    diagnoses_count = len(flat_actual_diagnoses)
    return {
        "traceability_rate": traceable / diagnoses_count,
        "evidence_completeness_ratio": evidence_complete / diagnoses_count,
        "mean_evidence_count": mean(evidence_counts),
        "structured_evidence_ratio": structured / diagnoses_count,
        "counts": {
            "diagnoses": diagnoses_count,
            "traceable": traceable,
            "evidence_complete": evidence_complete,
            "structured": structured,
        },
    }


def compute_runtime_metrics(run_context: Dict[str, Any], runtime_events: List[Dict[str, Any]], mode: str) -> Dict[str, Any]:
    finished = [
        event
        for event in runtime_events
        if event.get("event") == "script_finished" and event.get("mode") == mode and event.get("status") == "success"
    ]
    l1_events = [event for event in finished if event.get("catalogue_level") == "level1"]
    l2_events = [event for event in finished if event.get("catalogue_level") == "level2"]

    detector_breakdown = {event["script_name"].replace(".py", ""): event.get("duration_ms", 0) for event in l1_events}
    diagnoser_breakdown = {event["script_name"].replace(".py", ""): event.get("duration_ms", 0) for event in l2_events}

    mas_start = run_context.get("mas_start_epoch_ms")
    last_end = max((event.get("end_epoch_ms", 0) for event in finished), default=None)
    end_to_end = None
    if mas_start is not None and last_end is not None and last_end >= mas_start:
        end_to_end = last_end - mas_start

    wait_overhead = None
    first_l2_start = min((event.get("start_epoch_ms", 0) for event in l2_events), default=None)
    last_l1_end = max((event.get("end_epoch_ms", 0) for event in l1_events), default=None)
    if first_l2_start is not None and last_l1_end is not None and first_l2_start >= last_l1_end:
        wait_overhead = first_l2_start - last_l1_end

    return {
        "end_to_end_runtime_ms": end_to_end,
        "mean_runtime_l1_ms": mean(detector_breakdown.values()) if detector_breakdown else None,
        "mean_runtime_l2_ms": mean(diagnoser_breakdown.values()) if diagnoser_breakdown else None,
        "controller_waiting_overhead_ms": wait_overhead,
        "detector_breakdown_ms": detector_breakdown,
        "diagnoser_breakdown_ms": diagnoser_breakdown,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute relevant KPI metrics for one MASynReas run.")
    parser.add_argument("--dataset-id", help="Dataset identifier, e.g. DS11_single_point_of_failure_basic")
    parser.add_argument("--mode", choices=("apriori", "aposteriori"), help="Execution mode")
    parser.add_argument("--datasets-root", default="datasets", help="Datasets root directory")
    parser.add_argument("--results-root", default="results", help="Results directory from the MAS run")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    results_root = Path(args.results_root).resolve()
    datasets_root = Path(args.datasets_root).resolve()

    dataset_id, mode, run_context = infer_dataset_and_mode(results_root, args.dataset_id, args.mode)
    dataset = load_dataset_expectations(datasets_root, dataset_id)
    expected_level1 = dataset["expected_level1"]
    expected_level2 = dataset["expected_level2"]

    actual_level1 = load_actual_level1(results_root, mode)
    actual_level2 = load_actual_level2(results_root, mode)
    flat_actual_diagnoses = flatten_actual_diagnoses(actual_level2)
    runtime_events = load_runtime_events(results_root)

    expected_l1 = expected_l1_counts(expected_level1, mode)
    expected_l2 = expected_l2_entries(expected_level2, mode)
    expected_diag_keys = expected_l2_keys(expected_level2, mode)
    actual_diag_keys = actual_l2_keys(flat_actual_diagnoses)

    l1_match_value, l1_match_details = compute_l1_expectation_match(expected_l1, actual_level1)
    activation_value, activation_details = compute_l2_activation(expected_l2, actual_level2)
    l2_matching = compute_l2_matching(expected_diag_keys, actual_diag_keys)
    traceability = compute_traceability(flat_actual_diagnoses)
    runtime = compute_runtime_metrics(run_context, runtime_events, mode)

    expected_key_set = set(expected_diag_keys)
    precision_value = None
    if l2_matching["actual_count"] > 0:
        precision_value = l2_matching["tp_count"] / (l2_matching["tp_count"] + l2_matching["fp_count"])

    top1_value = compute_top1(flat_actual_diagnoses, expected_key_set)
    mrr_value = compute_mrr(flat_actual_diagnoses, expected_key_set)

    diagnosis_hit = None
    if expected_diag_keys:
        diagnosis_hit = 1.0 if l2_matching["tp_count"] > 0 else 0.0

    clean_control_success = None
    if not expected_diag_keys:
        clean_control_success = 1.0 if not actual_diag_keys else 0.0

    metrics = [
        metric_record(
            metric_name="l1_expectation_match_rate",
            scope="level1_proxy",
            dataset_id=dataset_id,
            mode=mode,
            value=l1_match_value,
            unit="ratio",
            counts={"correct": l1_match_details["correct"], "total": l1_match_details["total"]},
            breakdown=l1_match_details["per_agent"],
        ),
        metric_record(
            metric_name="l2_activation_correctness",
            scope="level2",
            dataset_id=dataset_id,
            mode=mode,
            value=activation_value,
            unit="ratio",
            counts={"correct": activation_details["correct"], "total": activation_details["total"]},
            breakdown=activation_details["per_agent"],
        ),
        metric_record(
            metric_name="precision_l2",
            scope="level2",
            dataset_id=dataset_id,
            mode=mode,
            value=precision_value,
            unit="ratio",
            counts={
                "tp": l2_matching["tp_count"],
                "fp": l2_matching["fp_count"],
                "expected": l2_matching["expected_count"],
                "actual": l2_matching["actual_count"],
            },
            parameters={"matching_policy": "diagnoser_agent+target_id"},
        ),
        metric_record(
            metric_name="diagnosis_hit",
            scope="level2_helper",
            dataset_id=dataset_id,
            mode=mode,
            value=diagnosis_hit,
            unit="ratio",
            counts={"tp": l2_matching["tp_count"], "expected": l2_matching["expected_count"]},
        ),
        metric_record(
            metric_name="clean_control_success",
            scope="level2_helper",
            dataset_id=dataset_id,
            mode=mode,
            value=clean_control_success,
            unit="ratio",
            counts={"actual_diagnoses": l2_matching["actual_count"], "expected_diagnoses": l2_matching["expected_count"]},
        ),
        metric_record(
            metric_name="top1_accuracy",
            scope="level2",
            dataset_id=dataset_id,
            mode=mode,
            value=top1_value,
            unit="ratio",
        ),
        metric_record(
            metric_name="ranking_mrr",
            scope="level2",
            dataset_id=dataset_id,
            mode=mode,
            value=mrr_value,
            unit="ratio",
        ),
        metric_record(
            metric_name="end_to_end_runtime",
            scope="time_complexity",
            dataset_id=dataset_id,
            mode=mode,
            value=runtime["end_to_end_runtime_ms"],
            unit="milliseconds",
        ),
        metric_record(
            metric_name="mean_runtime_l1",
            scope="time_complexity",
            dataset_id=dataset_id,
            mode=mode,
            value=runtime["mean_runtime_l1_ms"],
            unit="milliseconds",
            breakdown=runtime["detector_breakdown_ms"],
        ),
        metric_record(
            metric_name="mean_runtime_l2",
            scope="time_complexity",
            dataset_id=dataset_id,
            mode=mode,
            value=runtime["mean_runtime_l2_ms"],
            unit="milliseconds",
            breakdown=runtime["diagnoser_breakdown_ms"],
        ),
        metric_record(
            metric_name="controller_waiting_overhead",
            scope="time_complexity",
            dataset_id=dataset_id,
            mode=mode,
            value=runtime["controller_waiting_overhead_ms"],
            unit="milliseconds",
        ),
        metric_record(
            metric_name="traceability_rate",
            scope="explainability",
            dataset_id=dataset_id,
            mode=mode,
            value=traceability["traceability_rate"],
            unit="ratio",
            counts=traceability["counts"],
        ),
        metric_record(
            metric_name="evidence_completeness_ratio",
            scope="explainability",
            dataset_id=dataset_id,
            mode=mode,
            value=traceability["evidence_completeness_ratio"],
            unit="ratio",
            counts=traceability["counts"],
        ),
        metric_record(
            metric_name="mean_evidence_count",
            scope="explainability",
            dataset_id=dataset_id,
            mode=mode,
            value=traceability["mean_evidence_count"],
            unit="count",
            counts=traceability["counts"],
        ),
        metric_record(
            metric_name="structured_evidence_ratio",
            scope="explainability",
            dataset_id=dataset_id,
            mode=mode,
            value=traceability["structured_evidence_ratio"],
            unit="ratio",
            counts=traceability["counts"],
        ),
    ]

    report = {
        "dataset_id": dataset_id,
        "mode": mode,
        "run_context": run_context,
        "selected_relevant_metrics": RELEVANT_METRICS,
        "helper_metrics": HELPER_METRICS,
        "details": {
            "manifest": dataset["manifest"],
            "expected_level2_keys": [{"agent": agent, "target_id": target} for agent, target in expected_diag_keys],
            "actual_level2_keys": [{"agent": agent, "target_id": target} for agent, target in actual_diag_keys],
            "matched_level2_keys": [{"agent": agent, "target_id": target} for agent, target in l2_matching["tp"]],
            "missed_level2_keys": [{"agent": agent, "target_id": target} for agent, target in l2_matching["missed"]],
            "unexpected_level2_keys": [{"agent": agent, "target_id": target} for agent, target in l2_matching["fp"]],
            "actual_flat_diagnoses": flat_actual_diagnoses,
            "runtime_summary": runtime,
        },
        "metrics": metrics,
    }

    output_path = Path(args.output).resolve() if args.output else (results_root / "metrics" / "run_kpi_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
