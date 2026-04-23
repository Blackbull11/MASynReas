from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "change_induced_incident_diagnoser"
MODE = "aposteriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

CHANGE = AnchorRule("ChangeRequest", ("change",))
CHANGE_PAIR = AnchorRule("ChangeRequest", ("change1", "change2"), True)
RELATED = AnchorRule("RelatedElement", ("relatedElement", "resource"))

INPUT_SPECS = (
    InputSpec("change_followed_by_incident_detector", "dynamic", MODE, "change_followed_by_incident_results", "primary", "a change is followed by an incident on a related element", (CHANGE, RELATED), ("temporal",)),
    InputSpec("change_overlap_conflict", "dynamic", MODE, "change_overlap_conflict_results", "primary", "changes overlap on the same related element", (CHANGE_PAIR, RELATED), ("temporal",)),
    InputSpec("change_linked_to_multiple_incidents_detector", "procedural", MODE, "change_linked_to_multiple_incidents_results", "primary", "one change is linked to multiple incidents", (CHANGE,), ("governance",)),
    InputSpec("critical_event_ticket_escalation_detector", "dynamic", MODE, "critical_event_ticket_escalation_results", "supporting", "incident escalation increases after the change context", (RELATED,), ("temporal",)),
    InputSpec("silent_degradation_after_change_detector", "dynamic", MODE, "silent_degradation_after_change_results", "supporting", "silent degradation appears after the change", (CHANGE, RELATED), ("temporal",)),
)


def activation_rule(candidate, summary, loaded):
    present = summary["present_agents"]
    if "change_followed_by_incident_detector" in present:
        return True
    return {
        "change_overlap_conflict",
        "change_linked_to_multiple_incidents_detector",
    }.issubset(present)


def candidate_rule(candidate, summary, loaded):
    present = summary["present_agents"]
    if {
        "change_overlap_conflict",
        "change_linked_to_multiple_incidents_detector",
    }.issubset(present):
        return True
    return "change_followed_by_incident_detector" in present and len(summary["present_agents"]) >= 2


def main() -> None:
    run_anchor_diagnoser(
        project_root=PROJECT_ROOT,
        output_path=OUTPUT_PATH,
        agent_name=AGENT_NAME,
        mode=MODE,
        diagnosis_type="change_induced_incident",
        diagnosis_prefix="L2-P2",
        diagnosis_label="Change-induced incident",
        recommended_action="Inspect the implicated change request timeline, overlapping interventions, and incident links before looking for unrelated root causes.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="No change-centered evidence is strong enough to implicate a change as a common cause.",
        reason_no_candidate="Change-related evidence was present but did not form a coherent diagnosis around one change or related element.",
        base_bonus=10,
    )


if __name__ == "__main__":
    main()
