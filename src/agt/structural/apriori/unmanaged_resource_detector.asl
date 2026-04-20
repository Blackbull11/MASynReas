/*
 * Unmanaged Resource Detector - Structural / A Priori
 *
 * This agent detects resources that are not assigned to any management unit
 * in the NORIA-O knowledge graph.
 *
 * Such resources may indicate missing ownership, incomplete governance
 * modeling, or escalation weaknesses in the ICT infrastructure.
 */

+selected_mode(apriori)
  <- .print("[UnmanagedResourceDetector] Starting detection...");
     run_python("src/agt/structural/apriori/unmanaged_resource_detector.py");
     .print("[UnmanagedResourceDetector] Detection finished.") .


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
