from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "service_cascade_diagnoser"
MODE = "aposteriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

SERVICE_SINGLE = AnchorRule("Service", ("service",))
SERVICE_MULTI = AnchorRule("Service", ("service1", "service2"), True)
MODULE = AnchorRule("ApplicationModule", ("module",))
APPLICATION = AnchorRule("Application", ("application",))
RESOURCE = AnchorRule("Resource", ("resource", "relatedElement"))

CORE_SERVICE_AGENTS = {
    "cascading_service_failure_detector",
    "hidden_service_dependency_detector",
    "module_level_incident_aggregation_detector",
    "service_impacted_by_multiple_resources_detector",
    "service_with_repeated_incident_detector",
}

INPUT_SPECS = (
    InputSpec("cascading_service_failure_detector", "functional", MODE, "cascading_service_failure_results", "primary", "shared support chains affect several services", (SERVICE_MULTI, MODULE, APPLICATION, RESOURCE), ("concentration",)),
    InputSpec("hidden_service_dependency_detector", "functional", MODE, "hidden_service_dependency_results", "primary", "hidden service dependencies concentrate impact", (SERVICE_SINGLE, SERVICE_MULTI, MODULE, APPLICATION), ("concentration",)),
    InputSpec("module_level_incident_aggregation_detector", "functional", MODE, "module_level_incident_aggregation_results", "primary", "incidents aggregate at module level", (MODULE, APPLICATION, SERVICE_SINGLE), ("concentration",)),
    InputSpec("service_impacted_by_multiple_resources_detector", "functional", MODE, "service_impacted_by_multiple_resources_results", "primary", "one service is impacted by several resources", (SERVICE_SINGLE, RESOURCE), ("criticality", "concentration")),
    InputSpec("service_with_repeated_incident_detector", "functional", MODE, "service_with_repeated_incident_results", "primary", "the same service suffers repeated incidents", (SERVICE_SINGLE,), ("temporal",)),
    InputSpec("incident_propagation_detector", "dynamic", MODE, "incident_propagation_results", "supporting", "incident propagation is visible across neighboring elements", (RESOURCE,), ("temporal",)),
    InputSpec("multi_element_synchronous_incident_detector", "dynamic", MODE, "multi_element_synchronous_incident_results", "supporting", "several elements fail synchronously", (RESOURCE,), ("temporal",)),
    InputSpec("parent_child_event_escalation_detector", "dynamic", MODE, "parent_child_event_results", "supporting", "parent-child event escalation reinforces propagation", (RESOURCE,), ("temporal",)),
    InputSpec("critical_event_ticket_escalation_detector", "dynamic", MODE, "critical_event_ticket_escalation_results", "supporting", "ticket escalation indicates growing service impact", (SERVICE_SINGLE, RESOURCE), ("temporal",)),
)


def activation_rule(candidate, summary, loaded):
    return len(summary["present_agents"] & CORE_SERVICE_AGENTS) >= 2


def candidate_rule(candidate, summary, loaded):
    return len(summary["primary_agents"]) >= 2 and len(summary["families"]) >= 1


def main() -> None:
    run_anchor_diagnoser(
        project_root=PROJECT_ROOT,
        output_path=OUTPUT_PATH,
        agent_name=AGENT_NAME,
        mode=MODE,
        diagnosis_type="service_cascade",
        diagnosis_prefix="L2-P3",
        diagnosis_label="Service cascade",
        recommended_action="Inspect the shared module, hidden dependency, and common support resources behind this service scope first.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="Functional and dynamic propagation signals do not yet converge on a service or module scope.",
        reason_no_candidate="Propagation evidence was present but did not identify a coherent service cascade anchor.",
        base_bonus=10,
    )


if __name__ == "__main__":
    main()
