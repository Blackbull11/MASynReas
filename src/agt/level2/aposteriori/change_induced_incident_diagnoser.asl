/*
 * Change Induced Incident Diagnoser - Level 2 / A Posteriori
 */

+!run
  <- .print("[ChangeInducedIncidentDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/aposteriori/change_induced_incident_diagnoser.py");
     .print("[ChangeInducedIncidentDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(change_induced_incident_diagnoser)).
