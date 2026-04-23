from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "structural_fragility_diagnoser"
MODE = "apriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

RESOURCE = AnchorRule("Resource", ("resource", "parent_resource", "child_resource", "relatedElement"))
APPLICATION = AnchorRule("Application", ("application",))
INTERFACE = AnchorRule("Interface", ("interface", "networkInterface"))
LINK = AnchorRule("NetworkLink", ("link", "networkLink"))

INPUT_SPECS = (
    InputSpec("orphan_resource_detector", "structural", MODE, "orphan_resource_results", "primary", "resource isolation is detected", (RESOURCE,)),
    InputSpec("missing_interface_detector", "structural", MODE, "missing_interface_results", "primary", "interface information is missing", (RESOURCE,)),
    InputSpec("orphan_interface_detector", "structural", MODE, "orphan_interface_results", "supporting", "interfaces appear unattached", (INTERFACE, RESOURCE)),
    InputSpec("unconnected_interface_detector", "structural", MODE, "unconnected_interface_results", "primary", "interfaces are not visibly connected", (INTERFACE, RESOURCE), ("concentration",)),
    InputSpec("incomplete_network_link_detector", "structural", MODE, "incomplete_network_link_results", "primary", "network links are incomplete", (LINK, RESOURCE), ("concentration",)),
    InputSpec("missing_parent_resource_detector", "structural", MODE, "missing_parent_resource_results", "supporting", "hierarchical parentage is incomplete", (RESOURCE,), ("governance",)),
    InputSpec("application_without_support_detector", "structural", MODE, "application_without_support_results", "primary", "application support visibility is missing", (APPLICATION,), ("governance",)),
    InputSpec("unmanaged_resource_detector", "structural", MODE, "unmanaged_resource_results", "supporting", "management assignment is absent", (RESOURCE,), ("governance",)),
    InputSpec("missing_redundancy_detector", "structural", MODE, "missing_redundancy_results", "primary", "redundancy is missing", (RESOURCE, APPLICATION), ("concentration",)),
    InputSpec("criticality_structural_weakness_detector", "structural", MODE, "criticality_structural_weakness_results", "primary", "critical support chains are weak", (RESOURCE, APPLICATION), ("criticality", "concentration")),
)


def activation_rule(candidate, summary, loaded):
    return len(summary["primary_agents"]) >= 2 or (
        len(summary["primary_agents"]) >= 1 and len(summary["supporting_agents"]) >= 1
    )


def candidate_rule(candidate, summary, loaded):
    return activation_rule(candidate, summary, loaded)


def main() -> None:
    run_anchor_diagnoser(
        project_root=PROJECT_ROOT,
        output_path=OUTPUT_PATH,
        agent_name=AGENT_NAME,
        mode=MODE,
        diagnosis_type="structural_fragility",
        diagnosis_prefix="L2-A1",
        diagnosis_label="Structural fragility",
        recommended_action="Inspect the support chain, topology completeness, redundancy, and management assignment for this anchor.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="No coherent anchor accumulates enough structural weakness evidence.",
        reason_no_candidate="Structural evidence was present but did not converge strongly enough on a shared anchor.",
        base_bonus=8,
    )


if __name__ == "__main__":
    main()
