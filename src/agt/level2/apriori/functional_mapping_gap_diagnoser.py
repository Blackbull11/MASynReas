from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "functional_mapping_gap_diagnoser"
MODE = "apriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

APPLICATION = AnchorRule("Application", ("application",))
SERVICE_SINGLE = AnchorRule("Service", ("service",))
SERVICE_MULTI = AnchorRule("Service", ("service1", "service2"), True)
MODULE = AnchorRule("ApplicationModule", ("module",))

INPUT_SPECS = (
    InputSpec("application_without_module_detector", "functional", MODE, "application_without_module_results", "primary", "applications have no modules", (APPLICATION,), ("governance",)),
    InputSpec("application_without_resource_detector", "functional", MODE, "application_without_resource_results", "primary", "applications have no mapped resources", (APPLICATION,), ("concentration",)),
    InputSpec("duplicated_functional_mapping_detector", "functional", MODE, "duplicated_functional_mapping_results", "primary", "functional mappings are duplicated", (APPLICATION, SERVICE_SINGLE, MODULE), ("governance",)),
    InputSpec("inconsistent_service_hierarchy_detector", "functional", MODE, "inconsistent_service_hierarchy_results", "primary", "service hierarchy is inconsistent", (SERVICE_SINGLE, SERVICE_MULTI), ("governance",)),
    InputSpec("over_concentrated_service_detector", "functional", MODE, "over_concentrated_service_results", "supporting", "service support is over-concentrated", (SERVICE_SINGLE, APPLICATION), ("concentration",)),
    InputSpec("service_without_application_detector", "functional", MODE, "service_without_application_results", "primary", "services lack mapped applications", (SERVICE_SINGLE,), ("governance",)),
    InputSpec("service_without_resource_coverage_detector", "functional", MODE, "service_without_resource_coverage_results", "primary", "services lack resource coverage", (SERVICE_SINGLE, SERVICE_MULTI, APPLICATION), ("concentration",)),
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
        diagnosis_type="functional_mapping_gap",
        diagnosis_prefix="L2-A5",
        diagnosis_label="Functional mapping gap",
        recommended_action="Review the service-application-resource mapping chain and remove ambiguous or incomplete functional links for this anchor.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="Functional mapping evidence does not yet reach the diagnosis threshold.",
        reason_no_candidate="Functional mapping evidence was present but did not align on a coherent application or service anchor.",
        base_bonus=8,
    )


if __name__ == "__main__":
    main()
