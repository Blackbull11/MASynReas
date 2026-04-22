/*
 * Inconsistent Service Hierarchy Detector - Functional / A Priori
 *
 * This level-1 executor agent detects modules linked to several parent
 * services, which may indicate an inconsistent service hierarchy.
 */

+selected_mode(apriori)
  <- .print("[InconsistentServiceHierarchyDetector] Starting detection...");
     run_python("src/agt/functional/apriori/inconsistent_service_hierarchy_detector.py");
     .print("[InconsistentServiceHierarchyDetector] Detection finished.").
