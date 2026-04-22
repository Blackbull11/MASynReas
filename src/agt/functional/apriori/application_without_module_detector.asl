/*
 * Application Without Module Detector - Functional / A Priori
 *
 * This level-1 executor agent detects applications that are not linked to
 * any functional module.
 */

+selected_mode(apriori)
  <- .print("[ApplicationWithoutModuleDetector] Starting detection...");
     run_python("src/agt/functional/apriori/application_without_module_detector.py");
     .print("[ApplicationWithoutModuleDetector] Detection finished.").
