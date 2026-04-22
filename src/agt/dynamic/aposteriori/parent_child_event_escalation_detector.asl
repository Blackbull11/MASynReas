/*
 * Parent Child Event Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects temporally close parent/child event
 * pairs affecting structurally related elements.
 */

+selected_mode(aposteriori)
  <- .print("[ParentChildEventDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/parent_child_event_escalation_detector.py");
     .print("[ParentChildEventDetector] Detection finished.").
