/*
 * Incident Without Ticket Detector - Procedural / A Posteriori
 *
 * This agent detects incident-like EventRecord instances that are not linked
 * to any TroubleTicket in the NORIA-O knowledge graph.
 *
 * Such events may indicate operational incidents that were observed by the
 * supervision system but never formalized in the incident management process,
 * leading to a loss of traceability and weaker diagnostic capability.
 */

+selected_mode(aposteriori)
  <- .print("[IncidentWithoutTicketDetector] Starting detection...");
     run_python("src/agt/procedural/aposteriori/incident_without_ticket_detector.py");
     .print("[IncidentWithoutTicketDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }