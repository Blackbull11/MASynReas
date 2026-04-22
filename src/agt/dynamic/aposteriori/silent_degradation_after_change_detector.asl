/*
 * Silent Degradation After Change Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects patterns where a completed change is
 * followed by a progressive accumulation of weak or non-critical events on
 * the same related element.
 */

+selected_mode(aposteriori)
  <- .print("[SilentDegradationAfterChangeDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/silent_degradation_after_change_detector.py");
     .print("[SilentDegradationAfterChangeDetector] Detection finished.").