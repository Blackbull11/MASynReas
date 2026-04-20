/*
 * Unconnected Interface Detector - Structural / A Priori
 *
 * This agent detects interfaces that are linked to a resource but not to any
 * network link in the knowledge graph.
 */

+selected_mode(apriori)
  <- .print("[UnconnectedInterfaceDetector] Starting detection...");
     run_python("src/agt/structural/apriori/unconnected_interface_detector.py");
     .print("[UnconnectedInterfaceDetector] Detection finished.") .


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
