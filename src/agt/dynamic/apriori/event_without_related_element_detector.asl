/*
 * Event Without Related Element Detector - Dynamic / A Priori
 *
 * This level-1 executor agent detects EventRecord instances that are not
 * linked to any related network element, making dynamic diagnosis difficult.
 */

+selected_mode(apriori)
  <- .print("[EventWithoutRelatedElementDetector] Starting detection...");
     run_python("src/agt/dynamic/apriori/event_without_related_element_detector.py");
     .print("[EventWithoutRelatedElementDetector] Detection finished.").
