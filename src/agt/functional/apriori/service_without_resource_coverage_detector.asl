/*
 * Service Without Resource Coverage Detector - Functional / A Priori
 *
 * This level-1 executor agent detects services whose applications do not
 * expose any visible resource coverage.
 */

+selected_mode(apriori)
  <- .print("[ServiceWithoutResourceCoverageDetector] Starting detection...");
     run_python("src/agt/functional/apriori/service_without_resource_coverage_detector.py");
     .print("[ServiceWithoutResourceCoverageDetector] Detection finished.").
