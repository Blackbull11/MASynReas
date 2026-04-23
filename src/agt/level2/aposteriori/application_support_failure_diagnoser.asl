/*
 * Application Support Failure Diagnoser - Level 2 / A Posteriori
 */

+!run
  <- .print("[ApplicationSupportFailureDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/aposteriori/application_support_failure_diagnoser.py");
     .print("[ApplicationSupportFailureDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(application_support_failure_diagnoser)).
