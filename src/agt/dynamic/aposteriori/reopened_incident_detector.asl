/*
 * Reopened Incident Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects incident recurrence patterns where
 * a recently closed trouble ticket is followed by a new active ticket on
 * the same related element.
 */

+selected_mode(aposteriori)
  <- .print("[ReopenedIncidentDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/reopened_incident_detector.py");
     .print("[ReopenedIncidentDetector] Detection finished.").