/*
 * Isolated Incident Resource Detector - Structural / A Posteriori
 *
 * This level-1 executor agent detects incident-related resources with little
 * or no network connectivity in the NORIA-O knowledge graph.
 */

+selected_mode(aposteriori)
  <- .print("[IsolatedIncidentResourceDetector] Starting detection...");
     run_python("src/agt/structural/aposteriori/isolated_incident_resource_detector.py");
     .print("[IsolatedIncidentResourceDetector] Detection finished.").
