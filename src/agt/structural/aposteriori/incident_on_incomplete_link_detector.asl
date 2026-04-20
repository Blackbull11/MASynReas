/*
 * Incident On Incomplete Link Detector - Structural / A Posteriori
 *
 * This level-1 executor agent detects incidents involving resources connected
 * to incomplete or partially terminated network links in the NORIA-O
 * knowledge graph.
 */

+selected_mode(aposteriori)
  <- .print("[IncidentOnIncompleteLinkDetector] Starting detection...");
     run_python("src/agt/structural/aposteriori/incident_on_incomplete_link_detector.py");
     .print("[IncidentOnIncompleteLinkDetector] Detection finished.").
