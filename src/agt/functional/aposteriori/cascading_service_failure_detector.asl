/*
 * Cascading Service Failure Detector - Functional / A Posteriori
 *
 * This agent detects situations where an event occurring on a technical
 * resource may propagate to multiple services through a shared application
 * and its modules.
 *
 * In the NORIA-O toy graph, this is operationalized as:
 * - an event is emitted by a resource,
 * - that resource supports an application,
 * - one module of that application is attached to at least two services.
 *
 * Such a pattern suggests that a failure affecting one support chain may
 * propagate functionally to multiple services, which is a useful proxy
 * for cascading service failure in a level-1 deterministic detector.
 */

+selected_mode(aposteriori)
  <- .print("[CascadingServiceFailureDetector] Starting detection...");
     run_python("src/agt/functional/aposteriori/cascading_service_failure_detector.py");
     .print("[CascadingServiceFailureDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }