/*
 * Ticket Without Linked Event Detector - Procedural / A Posteriori
 *
 * This agent detects TroubleTicket instances that are not linked
 * to any EventRecord in the NORIA-O knowledge graph.
 *
 * Such tickets may indicate incidents that were opened manually or
 * incompletely documented, without any observable event trace,
 * reducing the quality of diagnosis and operational traceability.
 */

+selected_mode(aposteriori)
  <- .print("[TicketWithoutLinkedEventDetector] Starting detection...");
     run_python("src/agt/procedural/aposteriori/ticket_without_linked_event_detector.py");
     .print("[TicketWithoutLinkedEventDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }