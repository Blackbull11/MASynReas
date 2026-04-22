/*
 * Incomplete Network Link Detector - Structural / A Priori
 *
 * This agent detects network links with fewer than two termination resources
 * in the knowledge graph.
 */

+selected_mode(apriori)
  <- .print("[IncompleteNetworkLinkDetector] Starting detection...");
     run_python("src/agt/structural/apriori/incomplete_network_link_detector.py");
     .print("[IncompleteNetworkLinkDetector] Detection finished.") .


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
