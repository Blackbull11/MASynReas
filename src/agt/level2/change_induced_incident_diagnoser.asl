/*
 * Change-Induced Incident Diagnoser - Level 2 / A Posteriori
 *
 * Correlates dynamic (change_followed_by_incident) and procedural
 * (change_linked_to_multiple_incidents) signals on the same change entity.
 */

+!run
  <- .print("[ChangeInducedIncidentDiagnoser] Starting correlation...");
     run_python("src/agt/level2/change_induced_incident_diagnoser.py");
     .print("[ChangeInducedIncidentDiagnoser] Done.");
     .send(level2_controller, tell, l2_agent_done(change_induced_incident_diagnoser)).
