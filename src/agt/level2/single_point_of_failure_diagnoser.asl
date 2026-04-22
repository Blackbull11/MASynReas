/*
 * Single Point of Failure Diagnoser - Level 2 / A Posteriori
 *
 * Triggered by level2_controller once all level-1 aposteriori agents finish.
 * Correlates isolated, non-redundant, and high-impact resource signals.
 */

+!run
  <- .print("[SinglePointOfFailureDiagnoser] Starting correlation...");
     run_python("src/agt/level2/single_point_of_failure_diagnoser.py");
     .print("[SinglePointOfFailureDiagnoser] Done.");
     .send(level2_controller, tell, l2_agent_done(single_point_of_failure_diagnoser)).
