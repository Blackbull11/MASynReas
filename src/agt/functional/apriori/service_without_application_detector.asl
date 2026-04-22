/*
 * Service Without Application Detector - Functional / A Priori
 *
 * This level-1 executor agent detects services that are not linked to any
 * application module.
 */

+selected_mode(apriori)
  <- .print("[ServiceWithoutApplicationDetector] Starting detection...");
     run_python("src/agt/functional/apriori/service_without_application_detector.py");
     .print("[ServiceWithoutApplicationDetector] Detection finished.").
