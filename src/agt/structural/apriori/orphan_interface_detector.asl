/*
 * Orphan Interface Detector - Structural / A Priori
 *
 * This agent detects network interfaces that are not attached to any resource.
 *
 * Such interfaces are structurally invalid and typically indicate
 * inconsistencies in the knowledge graph.
 */

+selected_mode(apriori)
  <- .print("[OrphanInterfaceDetector] Starting detection...");
     run_python("src/agt/structural/apriori/orphan_interface_detector.py");
     .print("[OrphanInterfaceDetector] Detection finished.") .


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
