/*
 * Orphan Resource Detector - Structural / A Priori
 *
 * This level-1 executor agent launches a Python script that queries the
 * NORIA-O knowledge graph to detect orphan resources.
 *
 * A resource is considered orphan when it is not connected to the expected
 * structural entities of the ICT network graph.
 *
 * This agent is intentionally simple:
 * - it executes one deterministic SPARQL query,
 * - it stores results in a JSON file,
 * - it can later be used as a building block for higher-level reasoning.
 */

+selected_mode(apriori)
  <- .print("[OrphanResourceDetector] Starting structural a priori detection...");
     run_python("src/agt/structural/apriori/orphan_resource_detector.py");
     .print("[OrphanResourceDetector] Detection finished.") .


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
