/*
 * Unstable Component Diagnoser - Level 2 / A Posteriori
 */

+!run
  <- .print("[UnstableComponentDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/aposteriori/unstable_component_diagnoser.py");
     .print("[UnstableComponentDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(unstable_component_diagnoser)).
