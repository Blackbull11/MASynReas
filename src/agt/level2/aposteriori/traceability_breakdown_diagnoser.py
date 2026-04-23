from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import InputSpec, compute_priority, export_results, load_level1_inputs


AGENT_NAME = "traceability_breakdown_diagnoser"
MODE = "aposteriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

INPUT_SPECS = (
    InputSpec("incident_without_ticket_detector", "procedural", MODE, "incident_without_ticket_results", "primary", "incidents exist without tickets", ()),
    InputSpec("ticket_without_linked_event_detector", "procedural", MODE, "ticket_without_linked_event_results", "primary", "tickets exist without linked events", ()),
    InputSpec("service_without_ticket_escalation_detector", "functional", MODE, "service_without_ticket_escalation_results", "primary", "service impact occurs without ticket escalation", ()),
    InputSpec("ticket_without_assigned_procedure_detector", "procedural", "apriori", "ticket_without_assigned_procedure_results", "supporting", "tickets have no assigned procedure", ()),
    InputSpec("critical_event_ticket_escalation_detector", "dynamic", MODE, "critical_event_ticket_escalation_results", "contextual", "critical event escalation provides operational context", ()),
)


def main() -> None:
    loaded = load_level1_inputs(PROJECT_ROOT, INPUT_SPECS)
    positive = {agent for agent, payload in loaded.items() if payload["records"]}
    primary_positive = {
        agent
        for agent, payload in loaded.items()
        if payload["records"] and payload["spec"].role == "primary"
    }

    if len(primary_positive) < 2:
        export_results(
            OUTPUT_PATH,
            AGENT_NAME,
            MODE,
            "not_triggered",
            "At least two traceability-breakdown primary signals are required.",
            [],
        )
        return

    total_records = sum(len(payload["records"]) for payload in loaded.values())
    breadth = 15 if total_records >= 6 else 10 if total_records >= 3 else 5
    governance = min(15, len(positive) * 5)
    temporal = 6 if "critical_event_ticket_escalation_detector" in positive else 0
    severity_score = min(100, breadth + governance + temporal + 10)
    reliability_score = min(100, len(primary_positive) * 20 + (10 if len(positive) >= 3 else 0) + 15)
    priority_score = compute_priority(reliability_score, severity_score)

    explanation = (
        "Traceability breakdown is diagnosed because several operational links are missing at once: "
        "incident-to-ticket creation, ticket-to-event linkage, or service escalation tracking."
    )

    diagnosis = {
        "diagnosis_id": "L2-P4-001",
        "diagnosis_type": "traceability_breakdown",
        "mode": MODE,
        "target_type": "OperationalScope",
        "target_id": "operational_process",
        "activation_status": "triggered",
        "reliability_score": reliability_score,
        "severity_score": severity_score,
        "priority_score": priority_score,
        "evidence": [
            {
                "level1_agent": agent,
                "role": loaded[agent]["spec"].role,
                "matched_anchor": "operational_process",
                "record_count": len(loaded[agent]["records"]),
                "family": loaded[agent]["spec"].family,
                "result_file": loaded[agent]["spec"].relative_path.as_posix(),
            }
            for agent in sorted(positive)
        ],
        "severity_factors": {
            "criticality": 0,
            "breadth": breadth,
            "concentration": 0,
            "temporal_aggravation": temporal,
            "governance_weakness": governance,
            "family_base_bonus": 10,
        },
        "criticalities": [],
        "explanation": explanation,
        "recommended_action": "Restore ticket-event linkage and service escalation traceability before deeper root-cause investigation.",
    }

    export_results(
        OUTPUT_PATH,
        AGENT_NAME,
        MODE,
        "triggered",
        "Several procedural traceability signals are simultaneously positive.",
        [diagnosis],
    )


if __name__ == "__main__":
    main()
