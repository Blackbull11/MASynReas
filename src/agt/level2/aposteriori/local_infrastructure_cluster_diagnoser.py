from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "local_infrastructure_cluster_diagnoser"
MODE = "aposteriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

LOCATION = AnchorRule("Location", ("location", "site", "room"))
RESOURCE = AnchorRule("Resource", ("resource", "relatedElement", "parentResource", "childResource"))
LINK = AnchorRule("NetworkLink", ("link", "networkLink"))

INPUT_SPECS = (
    InputSpec("spatial_incident_cluster_detector", "structural", MODE, "spatial_incident_cluster_results", "primary", "incidents cluster spatially", (LOCATION, RESOURCE), ("concentration",)),
    InputSpec("parent_child_event_escalation_detector", "dynamic", MODE, "parent_child_event_results", "primary", "parent-child escalation reveals a local disturbed zone", (RESOURCE,), ("temporal",)),
    InputSpec("incident_propagation_detector", "dynamic", MODE, "incident_propagation_results", "primary", "incidents propagate across neighboring elements", (RESOURCE,), ("temporal",)),
    InputSpec("multi_element_synchronous_incident_detector", "dynamic", MODE, "multi_element_synchronous_incident_results", "primary", "several nearby elements fail synchronously", (RESOURCE, LOCATION), ("temporal",)),
    InputSpec("incident_on_incomplete_link_detector", "structural", MODE, "incident_on_incomplete_link_results", "supporting", "incomplete links reinforce the local disturbance hypothesis", (RESOURCE, LINK), ("concentration",)),
    InputSpec("high_impact_resource_detector", "structural", MODE, "high_impact_resource_results", "contextual", "high-impact resources increase the urgency of the local cluster", (RESOURCE,), ("criticality",)),
)


def activation_rule(candidate, summary, loaded):
    present = summary["present_agents"]
    return "spatial_incident_cluster_detector" in present and len(present) >= 2


def candidate_rule(candidate, summary, loaded):
    return activation_rule(candidate, summary, loaded)


def main() -> None:
    run_anchor_diagnoser(
        project_root=PROJECT_ROOT,
        output_path=OUTPUT_PATH,
        agent_name=AGENT_NAME,
        mode=MODE,
        diagnosis_type="local_infrastructure_cluster",
        diagnosis_prefix="L2-P7",
        diagnosis_label="Local infrastructure cluster",
        recommended_action="Treat this location or local resource neighborhood as a common disturbed zone and inspect shared infrastructure first.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="No locality signal is reinforced strongly enough by neighboring incident patterns.",
        reason_no_candidate="Locality evidence was present but did not yield a coherent disturbed-zone diagnosis.",
        base_bonus=10,
    )


if __name__ == "__main__":
    main()
