/*
 * Structural Fragility Diagnoser - Level 2 / A Priori
 */

+!run
  <- .print("[StructuralFragilityDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/apriori/structural_fragility_diagnoser.py");
     .print("[StructuralFragilityDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(structural_fragility_diagnoser)).
