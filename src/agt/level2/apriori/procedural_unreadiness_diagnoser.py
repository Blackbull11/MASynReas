from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "procedural_unreadiness_diagnoser"
MODE = "apriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

CHANGE = AnchorRule("ChangeRequest", ("change", "changeRequest"))
TICKET = AnchorRule("TroubleTicket", ("ticket",))
PROCEDURE = AnchorRule("Procedure", ("procedure",))
RESOURCE_TYPE = AnchorRule("ResourceType", ("resourceType", "type"))

INPUT_SPECS = (
    InputSpec("change_request_without_scheduled_time_detector", "procedural", MODE, "change_request_without_scheduled_time_results", "primary", "changes are missing scheduling information", (CHANGE,), ("governance", "temporal")),
    InputSpec("procedure_not_linked_to_resource_type_detector", "procedural", MODE, "procedure_not_linked_to_resource_type_results", "primary", "procedures are not linked to resource types", (PROCEDURE, RESOURCE_TYPE), ("governance",)),
    InputSpec("ticket_without_assigned_procedure_detector", "procedural", MODE, "ticket_without_assigned_procedure_results", "primary", "tickets have no assigned procedure", (TICKET,), ("governance",)),
    InputSpec("change_without_effective_time_detector", "dynamic", MODE, "change_without_effective_time_results", "supporting", "effective change execution time is missing", (CHANGE,), ("temporal",)),
)


def activation_rule(candidate, summary, loaded):
    return len(summary["primary_agents"]) >= 1


def candidate_rule(candidate, summary, loaded):
    return len(summary["primary_agents"]) >= 1 and summary["total_records"] >= 1


def main() -> None:
    run_anchor_diagnoser(
        project_root=PROJECT_ROOT,
        output_path=OUTPUT_PATH,
        agent_name=AGENT_NAME,
        mode=MODE,
        diagnosis_type="procedural_unreadiness",
        diagnosis_prefix="L2-A4",
        diagnosis_label="Procedural unreadiness",
        recommended_action="Clarify operational procedures, scheduling, and ticket-to-procedure links for this anchor before incident pressure appears.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="Procedural preparedness weaknesses were not strong enough to trigger a diagnosis.",
        reason_no_candidate="Procedural evidence was present but did not form a stable operational diagnosis scope.",
        base_bonus=8,
    )


if __name__ == "__main__":
    main()
