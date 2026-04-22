/*
 * Change Followed By Incident Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects patterns where a ChangeRequest
 * is followed shortly afterwards by an EventRecord on the same related element.
 */

+selected_mode(aposteriori)
  <- .print("[ChangeFollowedByIncidentDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/change_followed_by_incident_detector.py");
     .print("[ChangeFollowedByIncidentDetector] Detection finished.").