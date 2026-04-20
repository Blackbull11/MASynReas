/*
 * Missing or Incomplete Redundancy Detector - Structural / A Priori
 *
 * This agent detects critical applications that appear to rely on too few
 * supporting resources in the NORIA-O knowledge graph.
 *
 * Such cases may indicate single points of failure, incomplete redundancy
 * modeling, or resilience weaknesses in the ICT architecture.
 */

+selected_mode(apriori)
  <- .print("[MissingRedundancyDetector] Starting detection...");
     run_python("src/agt/structural/apriori/missing_redundancy_detector.py");
     .print("[MissingRedundancyDetector] Detection finished.") .


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
