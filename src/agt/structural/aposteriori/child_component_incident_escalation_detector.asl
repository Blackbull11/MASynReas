/*
 * Child Component Incident Escalation Detector - Structural / A Posteriori
 *
 * This level-1 executor agent detects incidents affecting child components
 * whose parent resource is structurally critical in the NORIA-O knowledge
 * graph.
 */

+selected_mode(aposteriori)
  <- .print("[ChildComponentIncidentEscalationDetector] Starting detection...");
     run_python("src/agt/structural/aposteriori/child_component_incident_escalation_detector.py");
     .print("[ChildComponentIncidentEscalationDetector] Detection finished.").
