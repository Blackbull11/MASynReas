/*
 * Service Without Ticket Escalation Detector - Functional / A Posteriori
 *
 * This agent detects services that are impacted by technical events through
 * the functional chain (resource → application → module → service), but for
 * which no related trouble ticket has been opened on the supporting resources.
 *
 * Such patterns may indicate:
 * - missing escalation,
 * - incomplete incident handling,
 * - monitoring without operational follow-up,
 * - or weak coupling between supervision and ticketing.
 */

+selected_mode(aposteriori)
  <- .print("[ServiceWithoutTicketEscalationDetector] Starting detection...");
     run_python("src/agt/functional/aposteriori/service_without_ticket_escalation_detector.py");
     .print("[ServiceWithoutTicketEscalationDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }