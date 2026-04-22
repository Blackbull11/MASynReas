/*
 * Over Concentrated Service Detector - Functional / A Priori
 *
 * This level-1 executor agent detects services whose support is concentrated
 * on too few resources.
 */

+selected_mode(apriori)
  <- .print("[OverConcentratedServiceDetector] Starting detection...");
     run_python("src/agt/functional/apriori/over_concentrated_service_detector.py");
     .print("[OverConcentratedServiceDetector] Detection finished.").
