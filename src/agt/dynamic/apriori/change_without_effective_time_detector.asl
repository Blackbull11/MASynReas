/*
 * Change Without Effective Time Detector - Dynamic / A Priori
 *
 * This level-1 executor agent detects ChangeRequest instances that do not
 * provide complete effective execution times, making post-change temporal
 * diagnosis unreliable.
 */

+selected_mode(apriori)
  <- .print("[ChangeWithoutEffectiveTimeDetector] Starting detection...");
     run_python("src/agt/dynamic/apriori/change_without_effective_time_detector.py");
     .print("[ChangeWithoutEffectiveTimeDetector] Detection finished.").