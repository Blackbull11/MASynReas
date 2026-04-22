/*
 * Module Level Incident Aggregation Detector - Functional / A Posteriori
 *
 * This agent detects situations where multiple technical incidents can be
 * aggregated at the application-module level.
 *
 * In the NORIA-O graph, this is operationalized as:
 * - events originate from resources,
 * - these resources support an application,
 * - the application contains one or more modules,
 * - and several events are associated with the same application/module chain.
 *
 * Such a pattern suggests that repeated low-level incidents may correspond
 * to a higher-level functional issue at module level.
 */

+selected_mode(aposteriori)
  <- .print("[ModuleLevelIncidentAggregationDetector] Starting detection...");
     run_python("src/agt/functional/aposteriori/module_level_incident_aggregation_detector.py");
     .print("[ModuleLevelIncidentAggregationDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }