/*
 * Level 2 Controller
 *
 * Waits for the selected-mode level-1 catalogue to finish, then launches
 * the corresponding level-2 diagnosis family agents.
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
     .send(service_cascade_diagnoser, achieve, run);
     .send(traceability_breakdown_diagnoser, achieve, run);
     .send(unstable_component_diagnoser, achieve, run);
     .send(application_support_failure_diagnoser, achieve, run);
     .send(local_infrastructure_cluster_diagnoser, achieve, run).

+!launch_level2(apriori)
  <- .send(structural_fragility_diagnoser, achieve, run);
     .send(critical_service_exposure_diagnoser, achieve, run);
     .send(observability_gap_diagnoser, achieve, run);
     .send(procedural_unreadiness_diagnoser, achieve, run);
     .send(functional_mapping_gap_diagnoser, achieve, run).

// Level-2 agents notify us when done
+l2_agent_done(Name)[source(_)]
  <- .print("[Level2Controller] Level-2 agent done: ", Name);
     ?l2_count(N); N1 = N + 1; -+l2_count(N1);
     !maybe_shutdown.

+!maybe_shutdown
  : selected_mode(apriori) & l2_count(5)
  <- .print("[Level2Controller] All level-2 agents done. Stopping MAS.");
     .stopMAS.

+!maybe_shutdown
  : selected_mode(aposteriori) & l2_count(7)
  <- .print("[Level2Controller] All level-2 agents done.").

+!maybe_shutdown <- true.

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
