from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "single_point_of_failure_diagnoser"
MODE = "aposteriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

RESOURCE = AnchorRule("Resource", ("resource", "relatedElement", "parentResource", "childResource"))
LINK = AnchorRule("NetworkLink", ("link", "networkLink"))

INPUT_SPECS = (
    InputSpec("isolated_incident_resource_detector", "structural", MODE, "isolated_incident_resource_results", "primary", "incident resources appear isolated", (RESOURCE,), ("concentration",)),
    InputSpec("incident_on_incomplete_link_detector", "structural", MODE, "incident_on_incomplete_link_results", "primary", "incident resources sit on incomplete links", (RESOURCE, LINK), ("concentration",)),
    InputSpec("high_impact_resource_detector", "structural", MODE, "high_impact_resource_results", "primary", "incident resources have broad downstream impact", (RESOURCE,), ("criticality",)),
    InputSpec("no_redundancy_incident_detector", "structural", MODE, "no_redundancy_incident_results", "primary", "incident resources have no visible redundancy", (RESOURCE,), ("concentration",)),
    InputSpec("child_component_incident_escalation_detector", "structural", MODE, "child_component_incident_escalation_results", "supporting", "incidents escalate through child components", (RESOURCE,), ("concentration",)),
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
        diagnosis_type="single_point_of_failure",
        diagnosis_prefix="L2-P1",
        diagnosis_label="Single point of failure",
        recommended_action="Inspect this local component first for isolation, incomplete topology, and missing failover support.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="No resource concentrates enough structural incident evidence to suggest a single point of failure.",
        reason_no_candidate="Structural incident evidence was present but did not produce a coherent local failure anchor.",
        base_bonus=10,
    )


if __name__ == "__main__":
    main()
