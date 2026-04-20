/*
 * No Redundancy Incident Detector - Structural / A Posteriori
 *
 * This level-1 executor agent detects incidents affecting resources for which
 * no visible redundancy or failover support is present in the NORIA-O
 * knowledge graph.
 */

+selected_mode(aposteriori)
  <- .print("[NoRedundancyIncidentDetector] Starting detection...");
     run_python("src/agt/structural/aposteriori/no_redundancy_detector.py");
     .print("[NoRedundancyIncidentDetector] Detection finished.").
