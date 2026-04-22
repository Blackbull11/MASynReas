/*
 * Ticket Without Assigned Procedure Detector - Procedural / A Priori
 *
 * This agent detects TroubleTicket instances that are not associated
 * with any suggested or assigned operational procedure in the NORIA-O
 * knowledge graph.
 *
 * In practice, this detector operationalizes the notion of "assigned
 * procedure" through the absence of any procedure proposed from the
 * event(s) linked to the ticket.
 */

+selected_mode(apriori)
  <- .print("[TicketWithoutAssignedProcedureDetector] Starting detection...");
     run_python("src/agt/procedural/apriori/ticket_without_assigned_procedure_detector.py");
     .print("[TicketWithoutAssignedProcedureDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }