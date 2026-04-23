from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "critical_service_exposure_diagnoser"
MODE = "apriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

RESOURCE = AnchorRule("Resource", ("resource", "relatedElement"))
APPLICATION = AnchorRule("Application", ("application",))
SERVICE_SINGLE = AnchorRule("Service", ("service",))
SERVICE_MULTI = AnchorRule("Service", ("service1", "service2"), True)

STRUCTURAL_AGENTS = {
    "missing_redundancy_detector",
    "criticality_structural_weakness_detector",
    "application_without_support_detector",
}
FUNCTIONAL_AGENTS = {
    "application_without_module_detector",
    "application_without_resource_detector",
    "over_concentrated_service_detector",
    "service_without_application_detector",
    "service_without_resource_coverage_detector",
}

INPUT_SPECS = (
    InputSpec("missing_redundancy_detector", "structural", MODE, "missing_redundancy_results", "primary", "redundancy is missing in the support chain", (RESOURCE, APPLICATION), ("concentration",)),
    InputSpec("criticality_structural_weakness_detector", "structural", MODE, "criticality_structural_weakness_results", "primary", "criticality is paired with structural weakness", (RESOURCE, APPLICATION), ("criticality", "concentration")),
    InputSpec("application_without_support_detector", "structural", MODE, "application_without_support_results", "primary", "applications have no visible technical support", (APPLICATION,), ("governance",)),
    InputSpec("application_without_module_detector", "functional", MODE, "application_without_module_results", "supporting", "applications lack module decomposition", (APPLICATION,), ("governance",)),
    InputSpec("application_without_resource_detector", "functional", MODE, "application_without_resource_results", "primary", "applications have no mapped resources", (APPLICATION,), ("concentration",)),
    InputSpec("over_concentrated_service_detector", "functional", MODE, "over_concentrated_service_results", "primary", "service support is overly concentrated", (SERVICE_SINGLE, APPLICATION), ("concentration",)),
    InputSpec("service_without_application_detector", "functional", MODE, "service_without_application_results", "primary", "services have no mapped applications", (SERVICE_SINGLE,), ("governance",)),
    InputSpec("service_without_resource_coverage_detector", "functional", MODE, "service_without_resource_coverage_results", "primary", "services have no visible resource coverage", (SERVICE_SINGLE, SERVICE_MULTI, APPLICATION), ("concentration",)),
)


def activation_rule(candidate, summary, loaded):
    present = summary["present_agents"]
    return bool(present & STRUCTURAL_AGENTS) and bool(present & FUNCTIONAL_AGENTS)


def candidate_rule(candidate, summary, loaded):
    present = summary["present_agents"]
    return activation_rule(candidate, summary, loaded) and len(summary["primary_agents"]) >= 2


def main() -> None:
    run_anchor_diagnoser(
        project_root=PROJECT_ROOT,
        output_path=OUTPUT_PATH,
        agent_name=AGENT_NAME,
        mode=MODE,
        diagnosis_type="critical_service_exposure",
        diagnosis_prefix="L2-A2",
        diagnosis_label="Critical service exposure",
        recommended_action="Prioritize coverage and redundancy analysis for this application or service chain before an incident occurs.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="No anchor combines critical structural weakness with functional coverage gaps.",
        reason_no_candidate="Exposure-related evidence was present but did not form a strong application or service diagnosis.",
        base_bonus=10,
    )


if __name__ == "__main__":
    main()
