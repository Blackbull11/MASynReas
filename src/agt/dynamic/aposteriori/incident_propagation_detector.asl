/*
 * Incident Propagation Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects local incident propagation patterns,
 * where an event affecting one element is shortly followed by an event
 * affecting a structurally adjacent element.
 */

+selected_mode(aposteriori)
  <- .print("[IncidentPropagationDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/incident_propagation_detector.py");
     .print("[IncidentPropagationDetector] Detection finished.").