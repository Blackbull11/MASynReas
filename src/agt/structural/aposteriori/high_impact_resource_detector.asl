/*
 * High Impact Resource Detector - Structural / A Posteriori
 *
 * This level-1 executor agent detects incident-affected resources that occupy
 * a structurally central position in the NORIA-O knowledge graph.
 */

+selected_mode(aposteriori)
  <- .print("[HighImpactResourceDetector] Starting detection...");
     run_python("src/agt/structural/aposteriori/high_impact_resource_detector.py");
     .print("[HighImpactResourceDetector] Detection finished.").
