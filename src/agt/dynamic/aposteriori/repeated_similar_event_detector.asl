/*
 * Repeated Similar Event Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects repeated similar events affecting
 * the same related element within a short time window.
 */

+selected_mode(aposteriori)
  <- .print("[RepeatedSimilarEventDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/repeated_similar_event_detector.py");
     .print("[RepeatedSimilarEventDetector] Detection finished.").