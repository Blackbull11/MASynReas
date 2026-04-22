/*
 * Level 2 Controller
 *
 * Waits for all level-1 detectors to finish, then triggers level-2
 * correlation agents. In apriori mode, also handles MAS shutdown once
 * level-2 is complete (replacing the apriori_test_controller shutdown).
 */

l1_count(0).
l2_count(0).

+python_finished(ScriptPath, ExitCode)[artifact_id(_)]
  : not l2c_seen(ScriptPath)
  <- +l2c_seen(ScriptPath);
     ?l1_count(N); N1 = N + 1; -+l1_count(N1);
     !maybe_trigger_level2.

+python_failed(ScriptPath, ExitCode)[artifact_id(_)]
  : not l2c_seen(ScriptPath)
  <- +l2c_seen(ScriptPath);
     ?l1_count(N); N1 = N + 1; -+l1_count(N1);
     !maybe_trigger_level2.

+!maybe_trigger_level2
  : expected_mode_runs(_, Expected) & l1_count(Expected) & not l2_triggered
  <- +l2_triggered;
     ?selected_mode(Mode);
     .print("[Level2Controller] All level-1 detectors done. Launching level-2 for mode: ", Mode);
     !launch_level2(Mode).

+!maybe_trigger_level2 <- true.

+!launch_level2(aposteriori)
  <- .send(single_point_of_failure_diagnoser, achieve, run);
     .send(change_induced_incident_diagnoser, achieve, run);
     .send(traceability_breakdown_diagnoser, achieve, run).

+!launch_level2(apriori)
  <- .send(structural_fragility_diagnoser, achieve, run).

// Level-2 agents notify us when done
+l2_agent_done(Name)[source(_)]
  <- .print("[Level2Controller] Level-2 agent done: ", Name);
     ?l2_count(N); N1 = N + 1; -+l2_count(N1);
     !maybe_shutdown.

+!maybe_shutdown
  : selected_mode(apriori) & l2_count(1)
  <- .print("[Level2Controller] All level-2 agents done. Stopping MAS.");
     .stopMAS.

+!maybe_shutdown
  : selected_mode(aposteriori) & l2_count(3)
  <- .print("[Level2Controller] All level-2 agents done.").

+!maybe_shutdown <- true.

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
