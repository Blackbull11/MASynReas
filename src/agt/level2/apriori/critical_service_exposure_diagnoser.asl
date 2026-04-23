/*
 * Critical Service Exposure Diagnoser - Level 2 / A Priori
 */

+!run
  <- .print("[CriticalServiceExposureDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/apriori/critical_service_exposure_diagnoser.py");
     .print("[CriticalServiceExposureDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(critical_service_exposure_diagnoser)).
