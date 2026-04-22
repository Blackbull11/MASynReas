/*
 * Critical Event Ticket Escalation Detector - Dynamic / A Posteriori
 *
 * This level-1 executor agent detects patterns where a critical-like event
 * is followed by the opening of a high-severity / high-priority / high-urgency
 * trouble ticket triggered by that event.
 */

+selected_mode(aposteriori)
  <- .print("[CriticalEventTicketEscalationDetector] Starting detection...");
     run_python("src/agt/dynamic/aposteriori/critical_event_ticket_escalation_detector.py");
     .print("[CriticalEventTicketEscalationDetector] Detection finished.").