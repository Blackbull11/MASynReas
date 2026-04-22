/*
 * Resource Event Without Service Impact Detector - Functional / A Posteriori
 *
 * This agent detects events occurring on resources that cannot be propagated
 * to any service through the functional chain (resource → application → module → service).
 *
 * Such patterns may indicate:
 * - isolated technical incidents,
 * - missing functional mapping,
 * - incomplete knowledge graph,
 * - or non-critical infrastructure alerts.
 */

+selected_mode(aposteriori)
  <- .print("[ResourceEventWithoutServiceImpactDetector] Starting detection...");
     run_python("src/agt/functional/aposteriori/resource_event_without_service_impact_detector.py");
     .print("[ResourceEventWithoutServiceImpactDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }