/*
 * Hidden Service Dependency Detector - Functional / A Posteriori
 *
 * This agent detects situations where a single technical incident may affect
 * multiple services through a shared application support chain, even though
 * no explicit dependency is modeled between these services.
 *
 * In the NORIA-O graph, this is operationalized as:
 * - an event originates from a resource,
 * - that resource supports an application,
 * - one module of that application is attached to two different services,
 * - and no explicit hierarchy/dependency relation is declared between them.
 *
 * Such a pattern may reveal an implicit or hidden dependency between services.
 */

+selected_mode(aposteriori)
  <- .print("[HiddenServiceDependencyDetector] Starting detection...");
     run_python("src/agt/functional/aposteriori/hidden_service_dependency_detector.py");
     .print("[HiddenServiceDependencyDetector] Detection finished.") .

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
