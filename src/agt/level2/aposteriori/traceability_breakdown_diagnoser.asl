/*
 * Traceability Breakdown Diagnoser - Level 2 / A Posteriori
 */

+!run
  <- .print("[TraceabilityBreakdownDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/aposteriori/traceability_breakdown_diagnoser.py");
     .print("[TraceabilityBreakdownDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(traceability_breakdown_diagnoser)).
