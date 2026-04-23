from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List


def load_report(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def metric_value(report: Dict[str, Any], metric_name: str) -> Any:
    for metric in report.get("metrics", []):
        if metric.get("metric_name") == metric_name:
            return metric
    return None


def applicable_values(reports: List[Dict[str, Any]], metric_name: str) -> List[float]:
    values: List[float] = []
    for report in reports:
        metric = metric_value(report, metric_name)
        if metric and metric.get("value") is not None:
            values.append(metric["value"])
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate KPI run reports across a dataset campaign.")
    parser.add_argument("--reports-dir", required=True, help="Directory containing run_kpi_report.json files")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir).resolve()
    report_paths = sorted(reports_dir.rglob("run_kpi_report.json"))
    reports = [load_report(path) for path in report_paths]

    diagnoser_frequency: Dict[str, Dict[str, int]] = defaultdict(lambda: {"matched": 0, "applicable": 0})
    clean_control_runs = 0
    clean_control_successes = 0

    tp_total = 0
    fp_total = 0
    activation_correct_total = 0
    activation_decisions_total = 0

    for report in reports:
        details = report.get("details", {})
        expected = details.get("expected_level2_keys", [])
        matched = details.get("matched_level2_keys", [])

        if not expected:
            clean_control_runs += 1
            clean_metric = metric_value(report, "clean_control_success")
            if clean_metric and clean_metric.get("value") == 1.0:
                clean_control_successes += 1

        for item in expected:
            diagnoser_frequency[item["agent"]]["applicable"] += 1

        matched_keys = {(item["agent"], item["target_id"]) for item in matched}
        for item in expected:
            if (item["agent"], item["target_id"]) in matched_keys:
                diagnoser_frequency[item["agent"]]["matched"] += 1

        precision_metric = metric_value(report, "precision_l2")
        if precision_metric:
            counts = precision_metric.get("counts", {})
            tp_total += counts.get("tp", 0)
            fp_total += counts.get("fp", 0)

        activation_metric = metric_value(report, "l2_activation_correctness")
        if activation_metric:
            counts = activation_metric.get("counts", {})
            activation_correct_total += counts.get("correct", 0)
            activation_decisions_total += counts.get("total", 0)

    aggregate = {
        "report_count": len(reports),
        "reports": [str(path) for path in report_paths],
        "metrics": {
            "diagnosis_success_rate": (
                mean(applicable_values(reports, "diagnosis_hit"))
                if applicable_values(reports, "diagnosis_hit")
                else None
            ),
            "clean_control_success_rate": (
                clean_control_successes / clean_control_runs if clean_control_runs else None
            ),
            "top1_accuracy": (
                mean(applicable_values(reports, "top1_accuracy"))
                if applicable_values(reports, "top1_accuracy")
                else None
            ),
            "ranking_mrr": (
                mean(applicable_values(reports, "ranking_mrr"))
                if applicable_values(reports, "ranking_mrr")
                else None
            ),
            "precision_l2_micro": (
                tp_total / (tp_total + fp_total) if (tp_total + fp_total) else None
            ),
            "l2_activation_correctness_micro": (
                activation_correct_total / activation_decisions_total if activation_decisions_total else None
            ),
            "traceability_rate_mean": (
                mean(applicable_values(reports, "traceability_rate"))
                if applicable_values(reports, "traceability_rate")
                else None
            ),
            "end_to_end_runtime_mean_ms": (
                mean(applicable_values(reports, "end_to_end_runtime"))
                if applicable_values(reports, "end_to_end_runtime")
                else None
            ),
            "mean_runtime_l1_mean_ms": (
                mean(applicable_values(reports, "mean_runtime_l1"))
                if applicable_values(reports, "mean_runtime_l1")
                else None
            ),
            "mean_runtime_l2_mean_ms": (
                mean(applicable_values(reports, "mean_runtime_l2"))
                if applicable_values(reports, "mean_runtime_l2")
                else None
            ),
            "controller_waiting_overhead_mean_ms": (
                mean(applicable_values(reports, "controller_waiting_overhead"))
                if applicable_values(reports, "controller_waiting_overhead")
                else None
            ),
        },
        "diagnoser_frequency_rate": {
            agent: (
                values["matched"] / values["applicable"] if values["applicable"] else None
            )
            for agent, values in sorted(diagnoser_frequency.items())
        },
    }

    output_path = Path(args.output).resolve() if args.output else (reports_dir / "campaign_kpi_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
