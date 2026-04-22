/*
 * Change Request Without Scheduled Time Detector - Procedural / A Priori
 *
 * This agent detects ChangeRequest instances that do not have any
 * scheduled execution time in the NORIA-O knowledge graph.
 *
 * Such changes may indicate poor planning and can introduce risks
 * when executed without a defined time window.
 */

+selected_mode(apriori)
  <- .print("[ChangeRequestWithoutScheduledTimeDetector] Starting detection...");
     run_python("src/agt/procedural/apriori/change_request_without_scheduled_time_detector.py");
     .print("[ChangeRequestWithoutScheduledTimeDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }