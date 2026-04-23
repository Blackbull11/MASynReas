/*
 * Service Cascade Diagnoser - Level 2 / A Posteriori
 */

+!run
  <- .print("[ServiceCascadeDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/aposteriori/service_cascade_diagnoser.py");
     .print("[ServiceCascadeDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(service_cascade_diagnoser)).
