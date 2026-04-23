from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "unstable_component_diagnoser"
MODE = "aposteriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

RESOURCE = AnchorRule("Resource", ("resource", "relatedElement"))
APPLICATION = AnchorRule("Application", ("application",))
TICKET = AnchorRule("TroubleTicket", ("ticket",))
EVENT = AnchorRule("Event", ("event",))

INPUT_SPECS = (
    InputSpec("event_burst_detector", "dynamic", MODE, "event_burst_results", "primary", "event bursts indicate repeated local disruption", (RESOURCE, EVENT), ("temporal",)),
    InputSpec("repeated_similar_event_detector", "dynamic", MODE, "repeated_similar_event_results", "primary", "similar events repeat on the same scope", (RESOURCE, EVENT), ("temporal",)),
    InputSpec("flapping_state_detector", "dynamic", MODE, "flapping_state_results", "primary", "state flapping indicates instability", (RESOURCE, EVENT, APPLICATION), ("temporal",)),
    InputSpec("reopened_incident_detector", "dynamic", MODE, "reopened_incident_results", "primary", "incidents reopen after apparent closure", (TICKET, RESOURCE, APPLICATION), ("temporal", "governance")),
    InputSpec("stale_incident_detector", "dynamic", MODE, "stale_incident_results", "primary", "incidents remain stale and unresolved", (TICKET, RESOURCE, APPLICATION), ("temporal", "governance")),
)


def activation_rule(candidate, summary, loaded):
    return len(summary["primary_agents"]) >= 2


def candidate_rule(candidate, summary, loaded):
    return len(summary["primary_agents"]) >= 2


def main() -> None:
    run_anchor_diagnoser(
        project_root=PROJECT_ROOT,
        output_path=OUTPUT_PATH,
        agent_name=AGENT_NAME,
        mode=MODE,
        diagnosis_type="unstable_component",
        diagnosis_prefix="L2-P5",
        diagnosis_label="Unstable component",
        recommended_action="Treat this component as chronically unstable and inspect recurrence, flapping, and unresolved-incident history together.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="Recurrent incident evidence does not yet converge on a shared component scope.",
        reason_no_candidate="Recurrence evidence was present but did not produce a coherent unstable-component anchor.",
        base_bonus=9,
    )


if __name__ == "__main__":
    main()
