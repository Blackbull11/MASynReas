/*
 * Change Overlap Conflict Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects overlapping ChangeRequest instances
 * affecting the same related element.
 */

+selected_mode(aposteriori)
  <- .print("[ChangeOverlapConflictDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/change_overlap_conflict.py");
     .print("[ChangeOverlapConflictDetector] Detection finished.").
