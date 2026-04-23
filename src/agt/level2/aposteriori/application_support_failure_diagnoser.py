from __future__ import annotations

import sys
from pathlib import Path

LEVEL2_ROOT = Path(__file__).resolve().parents[1]
if str(LEVEL2_ROOT) not in sys.path:
    sys.path.append(str(LEVEL2_ROOT))

from common import AnchorRule, InputSpec, run_anchor_diagnoser


AGENT_NAME = "application_support_failure_diagnoser"
MODE = "aposteriori"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_PATH = PROJECT_ROOT / "results" / "level2" / MODE / f"{AGENT_NAME}.json"

APPLICATION = AnchorRule("Application", ("application",))
RESOURCE = AnchorRule("Resource", ("resource", "relatedElement"))
SERVICE = AnchorRule("Service", ("service", "service1", "service2"), True)

APP_ANOMALY_AGENTS = {
    "application_incident_without_resource_detector",
    "conflicting_application_state_detector",
}
SUPPORT_AGENTS = {
    "application_mapping_inconsistency_detector",
    "resource_event_without_service_impact_detector",
}

INPUT_SPECS = (
    InputSpec("application_incident_without_resource_detector", "functional", MODE, "application_incident_without_resource_results", "primary", "applications show incidents without mapped resources", (APPLICATION,), ("concentration",)),
    InputSpec("application_mapping_inconsistency_detector", "structural", MODE, "application_mapping_inconsistency_results", "primary", "application support mapping is inconsistent", (APPLICATION, RESOURCE), ("governance",)),
    InputSpec("resource_event_without_service_impact_detector", "functional", MODE, "resource_event_without_service_impact_results", "primary", "resource events lack visible service impact mapping", (RESOURCE, SERVICE, APPLICATION), ("governance",)),
    InputSpec("conflicting_application_state_detector", "functional", MODE, "conflicting_application_state_results", "primary", "application state is contradictory", (APPLICATION,), ("temporal",)),
)


def activation_rule(candidate, summary, loaded):
    present = summary["present_agents"]
    return bool(present & APP_ANOMALY_AGENTS) and bool(present & SUPPORT_AGENTS)


def candidate_rule(candidate, summary, loaded):
    return activation_rule(candidate, summary, loaded)


def main() -> None:
    run_anchor_diagnoser(
        project_root=PROJECT_ROOT,
        output_path=OUTPUT_PATH,
        agent_name=AGENT_NAME,
        mode=MODE,
        diagnosis_type="application_support_failure",
        diagnosis_prefix="L2-P6",
        diagnosis_label="Application support failure",
        recommended_action="Reconcile application incidents with the underlying support mapping before escalating further symptoms.",
        input_specs=INPUT_SPECS,
        activation_predicate=activation_rule,
        candidate_predicate=candidate_rule,
        reason_not_triggered="Application anomalies do not yet align with support-chain inconsistencies.",
        reason_no_candidate="Application-level evidence was present but did not converge on a coherent support-failure anchor.",
        base_bonus=9,
    )


if __name__ == "__main__":
    main()
