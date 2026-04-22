/*
 * Stale Incident Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects persistent incidents, i.e. active
 * trouble tickets that remain unresolved while new events continue to be
 * observed on the same related element.
 */

+selected_mode(aposteriori)
  <- .print("[StaleIncidentDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/stale_incident_detector.py");
     .print("[StaleIncidentDetector] Detection finished.").