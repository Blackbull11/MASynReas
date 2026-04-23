from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "observability_gap_diagnoser"
MODE = "apriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

EVENT = AnchorRule("Event", ("event",))
CHANGE = AnchorRule("ChangeRequest", ("change", "changeRequest"))
RELATED = AnchorRule("RelatedElement", ("relatedElement", "resource", "application"))

INPUT_SPECS = (
    InputSpec("event_without_timestamp_detector", "dynamic", MODE, "event_without_timestamp_results", "primary", "event timestamps are missing", (EVENT, RELATED), ("temporal",)),
    InputSpec("event_without_related_element_detector", "dynamic", MODE, "event_without_related_element_results", "primary", "events are missing related elements", (EVENT,), ("governance",)),
    InputSpec("change_without_effective_time_detector", "dynamic", MODE, "change_without_effective_time_results", "primary", "changes have no effective execution time", (CHANGE, RELATED), ("temporal",)),
    InputSpec("change_request_without_scheduled_time_detector", "procedural", MODE, "change_request_without_scheduled_time_results", "supporting", "changes have no scheduled time", (CHANGE,), ("governance",)),
)


def activation_rule(candidate, summary, loaded):
    return len(summary["present_agents"]) >= 2


def candidate_rule(candidate, summary, loaded):
    return len(summary["primary_agents"]) >= 2 or (
        len(summary["primary_agents"]) >= 1 and len(summary["supporting_agents"]) >= 1
    )


def main() -> None:
    run_anchor_diagnoser(
        project_root=PROJECT_ROOT,
        output_path=OUTPUT_PATH,
        agent_name=AGENT_NAME,
        mode=MODE,
        diagnosis_type="observability_gap",
        diagnosis_prefix="L2-A3",
        diagnosis_label="Observability gap",
        recommended_action="Improve timestamps, related-element links, and change scheduling metadata for this scope before relying on later diagnosis.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="Observability evidence does not yet converge strongly enough on any event or change scope.",
        reason_no_candidate="Observability signals were present but did not produce a coherent diagnosis anchor.",
        base_bonus=7,
    )


if __name__ == "__main__":
    main()
