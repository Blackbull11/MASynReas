/*
 * Traceability Breakdown Diagnoser - Level 2 / A Posteriori
 *
 * Correlates procedural signals: incidents without tickets and
 * tickets without linked events — both indicate broken traceability chains.
 */

+!run
  <- .print("[TraceabilityBreakdownDiagnoser] Starting correlation...");
     run_python("src/agt/level2/traceability_breakdown_diagnoser.py");
     .print("[TraceabilityBreakdownDiagnoser] Done.");
     .send(level2_controller, tell, l2_agent_done(traceability_breakdown_diagnoser)).
