/*
 * Missing Network Interface Detector - Structural / A Priori
 *
 * This agent detects resources that do not expose any explicit network
 * interface in the knowledge graph.
 */

+selected_mode(apriori)
  <- .print("[MissingInterfaceDetector] Starting detection...");
     run_python("src/agt/structural/apriori/missing_interface_detector.py");
     .print("[MissingInterfaceDetector] Detection finished.") .


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
