/*
 * Application Without Infrastructure Support Detector - Structural / A Priori
 *
 * This agent detects applications that are not linked to any supporting
 * technical resource in the NORIA-O knowledge graph.
 *
 * Such applications may indicate missing deployment information, incomplete
 * functional-to-technical mapping, or architectural inconsistencies.
 */

+selected_mode(apriori)
  <- .print("[ApplicationWithoutSupportDetector] Starting detection...");
     run_python("src/agt/structural/apriori/application_without_support_detector.py");
     .print("[ApplicationWithoutSupportDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
