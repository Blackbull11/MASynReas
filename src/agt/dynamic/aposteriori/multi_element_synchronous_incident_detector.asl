/*
 * Multi Element Synchronous Incident Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects patterns where several distinct
 * related elements are affected by EventRecord instances within a short
 * common time window.
 */

+selected_mode(aposteriori)
  <- .print("[MultiElementSynchronousIncidentDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/multi_element_synchronous_incident_detector.py");
     .print("[MultiElementSynchronousIncidentDetector] Detection finished.").