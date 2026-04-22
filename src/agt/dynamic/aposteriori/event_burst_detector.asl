/*
 * Event Burst Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects burst patterns of EventRecord instances
 * affecting the same related element within a short time window.
 */

+selected_mode(aposteriori)
  <- .print("[EventBurstDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/event_burst_detector.py");
     .print("[EventBurstDetector] Detection finished.").