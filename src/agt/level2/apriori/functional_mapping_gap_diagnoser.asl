/*
 * Functional Mapping Gap Diagnoser - Level 2 / A Priori
 */

+!run
  <- .print("[FunctionalMappingGapDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/apriori/functional_mapping_gap_diagnoser.py");
     .print("[FunctionalMappingGapDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(functional_mapping_gap_diagnoser)).
