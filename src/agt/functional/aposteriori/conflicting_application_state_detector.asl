/*
 * Conflicting Application State Detector - Functional / A Posteriori
 *
 * This agent detects applications that appear in conflicting operational
 * states at the same time, based on event types.
 *
 * A conflict is identified when multiple events with different types are
 * associated to the same application at the same timestamp.
 */

+selected_mode(aposteriori)
  <- .print("[ConflictingApplicationStateDetector] Starting detection...");
     run_python("src/agt/functional/aposteriori/conflicting_application_state_detector.py");
     .print("[ConflictingApplicationStateDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }