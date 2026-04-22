/*
 * Flapping State Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects rapid alternation of contradictory
 * state-related events (e.g. UP/DOWN) affecting the same related element.
 */

+selected_mode(aposteriori)
  <- .print("[FlappingStateDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/flapping_state_detector.py");
     .print("[FlappingStateDetector] Detection finished.").