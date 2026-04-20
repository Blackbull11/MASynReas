/*
 * Application Mapping Inconsistency Detector - Structural / A Posteriori
 *
 * This level-1 executor agent detects incidents involving applications whose
 * technical support mapping is incomplete or ambiguous in the NORIA-O
 * knowledge graph.
 */

+selected_mode(aposteriori)
  <- .print("[ApplicationMappingInconsistencyDetector] Starting detection...");
     run_python("src/agt/structural/aposteriori/application_mapping_inconsistency_detector.py");
     .print("[ApplicationMappingInconsistencyDetector] Detection finished.").
