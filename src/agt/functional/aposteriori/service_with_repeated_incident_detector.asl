/*
 * Service With Repeated Incident Detector - Functional / A Posteriori
 *
 * This agent detects services that are impacted repeatedly by technical events
 * through the functional chain (resource → application → module → service).
 *
 * Such patterns may indicate:
 * - chronic service fragility,
 * - recurring degradation,
 * - repeated infrastructure stress,
 * - or unresolved root causes.
 */

+selected_mode(aposteriori)
  <- .print("[ServiceWithRepeatedIncidentDetector] Starting detection...");
     run_python("src/agt/functional/aposteriori/service_with_repeated_incident_detector.py");
     .print("[ServiceWithRepeatedIncidentDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }