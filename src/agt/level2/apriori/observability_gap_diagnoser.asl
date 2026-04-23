/*
 * Observability Gap Diagnoser - Level 2 / A Priori
 */

+!run
  <- .print("[ObservabilityGapDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/apriori/observability_gap_diagnoser.py");
     .print("[ObservabilityGapDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(observability_gap_diagnoser)).
