/*
 * Service Without Application Detector - Functional / A Priori
 *
 * Planned level-1 detector for services that are not linked to any
 * application module.
 */

+selected_mode(apriori)
  <- .print("[ServiceWithoutApplicationDetector] Starting detection...");
     run_python("src/agt/functional/apriori/service_without_application_detector.py");
     .print("[ServiceWithoutApplicationDetector] Detection finished.").
