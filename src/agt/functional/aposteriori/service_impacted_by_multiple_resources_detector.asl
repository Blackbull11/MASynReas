/*
 * Service Impacted By Multiple Resources Detector - Functional / A Posteriori
 *
 * This agent detects services that are impacted by multiple distinct resources
 * through the functional chain (resource → application → module → service).
 *
 * Such patterns typically indicate:
 * - major incidents,
 * - distributed failures,
 * - or systemic degradation affecting a service.
 */

+selected_mode(aposteriori)
  <- .print("[ServiceImpactedByMultipleResourcesDetector] Starting detection...");
     run_python("src/agt/functional/aposteriori/service_impacted_by_multiple_resources_detector.py");
     .print("[ServiceImpactedByMultipleResourcesDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }