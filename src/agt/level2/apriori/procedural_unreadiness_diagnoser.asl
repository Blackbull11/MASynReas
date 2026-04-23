/*
 * Procedural Unreadiness Diagnoser - Level 2 / A Priori
 */

+!run
  <- .print("[ProceduralUnreadinessDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/apriori/procedural_unreadiness_diagnoser.py");
     .print("[ProceduralUnreadinessDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(procedural_unreadiness_diagnoser)).
