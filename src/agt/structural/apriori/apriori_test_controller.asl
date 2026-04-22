/*
 * Structural Test Controller
 *
 * This agent watches the shared Python execution artifact and stops the MAS
 * once every structural detector has reported either success or failure.
 */

completed(0).

+selected_mode(apriori)
  <- .print("[AprioriTestController] Running in apriori mode. Waiting for detector completions...").

+selected_mode(aposteriori)
  <- .print("[AprioriTestController] Running in aposteriori mode. Automatic shutdown is disabled.").

+python_finished(ScriptPath, ExitCode)[artifact_id(_)]
  : not processed(ScriptPath)
  <- +processed(ScriptPath);
     ?completed(Count);
     NewCount = Count + 1;
     -completed(Count);
     +completed(NewCount);
     .print("[AprioriTestController] Completed ", ScriptPath, " with exit code ", ExitCode, ".");
     !check_shutdown.

+python_failed(ScriptPath, ExitCode)[artifact_id(_)]
  : not processed(ScriptPath)
  <- +processed(ScriptPath);
     ?completed(Count);
     NewCount = Count + 1;
     -completed(Count);
     +completed(NewCount);
     .print("[AprioriTestController] Failed ", ScriptPath, " with exit code ", ExitCode, ".");
     !check_shutdown.

+!check_shutdown
  : selected_mode(apriori) & expected_mode_runs(apriori, Expected) & completed(Expected)
  <- .print("[AprioriTestController] All apriori level-1 detectors reported. Waiting for level-2...").

+!check_shutdown
  <- true.

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
