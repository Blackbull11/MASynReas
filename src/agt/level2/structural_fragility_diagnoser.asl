/*
 * Structural Fragility Diagnoser - Level 2 / A Priori
 *
 * Correlates multiple structural a priori weakness signals on the same
 * resource: orphan, missing interface, unmanaged, missing parent.
 * Resources appearing in 2+ files are diagnosed as structurally fragile.
 */

+!run
  <- .print("[StructuralFragilityDiagnoser] Starting correlation...");
     run_python("src/agt/level2/structural_fragility_diagnoser.py");
     .print("[StructuralFragilityDiagnoser] Done.");
     .send(level2_controller, tell, l2_agent_done(structural_fragility_diagnoser)).
