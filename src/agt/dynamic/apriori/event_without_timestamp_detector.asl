/*
 * Event Without Timestamp Detector - Dynamic / A Priori
 *
 * This level-1 executor agent detects EventRecord instances that do not
 * provide any logging timestamp, making temporal reasoning impossible.
 */

+selected_mode(apriori)
  <- .print("[EventWithoutTimestampDetector] Starting detection...");
     run_python("src/agt/dynamic/apriori/event_without_timestamp_detector.py");
     .print("[EventWithoutTimestampDetector] Detection finished.").
