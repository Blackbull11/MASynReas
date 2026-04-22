/*
 * Missing Parent Resource Detector - Structural / A Priori
 *
 * This agent detects component-like resources that do not have any structural
 * parent in the knowledge graph.
 */

+selected_mode(apriori)
  <- .print("[MissingParentResourceDetector] Starting detection...");
     run_python("src/agt/structural/apriori/missing_parent_resource_detector.py");
     .print("[MissingParentResourceDetector] Detection finished.") .


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
