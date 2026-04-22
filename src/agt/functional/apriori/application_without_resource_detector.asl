/*
 * Application Without Resource Detector - Functional / A Priori
 *
 * This level-1 executor agent detects applications that are not linked to
 * any supporting technical resource.
 */

+selected_mode(apriori)
  <- .print("[ApplicationWithoutResourceDetector] Starting detection...");
     run_python("src/agt/functional/apriori/application_without_resource_detector.py");
     .print("[ApplicationWithoutResourceDetector] Detection finished.").
