/*
 * Change Linked To Multiple Incidents Detector - Procedural / A Posteriori
 *
 * This agent detects ChangeRequest instances that are linked to several
 * TroubleTicket incidents in the NORIA-O knowledge graph.
 *
 * Such a pattern may indicate a risky or badly controlled change whose
 * execution triggered multiple operational incidents, or a change that
 * has been correlated too broadly and deserves further investigation.
 */

+selected_mode(aposteriori)
  <- .print("[ChangeLinkedToMultipleIncidentsDetector] Starting detection...");
     run_python("src/agt/procedural/aposteriori/change_linked_to_multiple_incidents_detector.py");
     .print("[ChangeLinkedToMultipleIncidentsDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }