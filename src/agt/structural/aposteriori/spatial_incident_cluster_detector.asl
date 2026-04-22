/*
 * Spatial Incident Cluster Detector - Structural / A Posteriori
 *
 * This level-1 executor agent detects clusters of incidents localized in the
 * same physical area in the NORIA-O knowledge graph.
 */

+selected_mode(aposteriori)
  <- .print("[SpatialIncidentClusterDetector] Starting detection...");
     run_python("src/agt/structural/aposteriori/spatial_incident_cluster_detector.py");
     .print("[SpatialIncidentClusterDetector] Detection finished.").
