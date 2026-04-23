/*
 * Single Point Of Failure Diagnoser - Level 2 / A Posteriori
 */

+!run
  <- .print("[SinglePointOfFailureDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/aposteriori/single_point_of_failure_diagnoser.py");
     .print("[SinglePointOfFailureDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(single_point_of_failure_diagnoser)).
