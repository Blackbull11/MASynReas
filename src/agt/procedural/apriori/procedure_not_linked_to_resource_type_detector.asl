/*
 * Procedure Not Linked To Resource Type Detector - Procedural / A Priori
 *
 * This agent detects procedures that are not linked to any resource type
 * in the NORIA-O knowledge graph.
 *
 * In practice, this detector operationalizes the notion of "linked to a
 * resource type" through the absence of any event recommending the procedure
 * on a resource carrying a noria:resourceType.
 */

+selected_mode(apriori)
  <- .print("[ProcedureNotLinkedToResourceTypeDetector] Starting detection...");
     run_python("src/agt/procedural/apriori/procedure_not_linked_to_resource_type_detector.py");
     .print("[ProcedureNotLinkedToResourceTypeDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }