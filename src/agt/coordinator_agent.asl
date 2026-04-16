critical_alarms([]).
propagations([]).
unhandled_alarms([]).
report_file("diagnostic_noria.txt").

!wait_for_results.

+!wait_for_results
  <- .print("=== Coordinator: en attente des 3 workers... ===").

+worker_done("critical_alarm_agent", Result)[source(Sender)]
    : not received_critical
  <- +received_critical;
     .print("Coordinator: alarmes critiques recues");
     -+critical_alarms(Result);
     !check_and_trigger.

+worker_done("critical_alarm_agent", Result)[source(Sender)]
    : received_critical <- true.

+worker_done("propagation_agent", Result)[source(Sender)]
    : not received_propagation
  <- +received_propagation;
     .print("Coordinator: propagations recues");
     -+propagations(Result);
     !check_and_trigger.

+worker_done("propagation_agent", Result)[source(Sender)]
    : received_propagation <- true.

+worker_done("unhandled_agent", Result)[source(Sender)]
    : not received_unhandled
  <- +received_unhandled;
     .print("Coordinator: alarmes non traitees recues");
     -+unhandled_alarms(Result);
     !check_and_trigger.

+worker_done("unhandled_agent", Result)[source(Sender)]
    : received_unhandled <- true.

+worker_error(Id, Msg)[source(Sender)]
  <- .print("Coordinator: ERREUR du worker ", Id, " : ", Msg);
     !check_and_trigger.

/* déclenche le diagnostic seulement quand les 3 flags sont posés */
+!check_and_trigger
  : received_critical & received_propagation & received_unhandled & not diagnosis_done
  <- +diagnosis_done.

+!check_and_trigger <- true.

/* réactif : fired exactement une fois quand diagnosis_done est ajouté */
+diagnosis_done
  <- .print("Coordinator: === demarrage du diagnostic ===");
     !run_diagnosis.

+!run_diagnosis
  <- !compute_severity(Severity, Reason, Action);
     .print("Coordinator: severite -> ", Severity);
     !write_report(Severity, Reason, Action);
     !run_narrative(Severity, Reason, Action).

+!run_narrative(Severity, Reason, Action)
  <- .print("Coordinator: lancement de la synthese narrative LLM...");
     execPython("diagnosis_llm.py", "result_narrative.txt");
     .print("");
     .print("=== DIAGNOSTIC GLOBAL NORIA ===");
     .print("Severite : ", Severity);
     .print("Raison   : ", Reason);
     .print("Action   : ", Action);
     .print("Narrative: voir diagnostic_noria.txt");
     .print("================================").

/* ignore les signaux query_result/query_error des scripts de detection */
+query_result(_) <- true.
+query_error(_)  <- true.

+!compute_severity(Severity, Reason, Action)
  <- ?propagations(P);
     ?unhandled_alarms(U);
     ?critical_alarms(A);
     if (P \== [] & U \== []) {
         Severity = "CRITIQUE";
         Reason   = "Panne propagee ET ressource sans plan de reparation";
         Action   = "Escalade immediate requise sur les deux equipes"
     } else { if (P \== []) {
         Severity = "MAJEURE";
         Reason   = "Panne confirmee avec propagation reseau";
         Action   = "Appliquer le plan de reparation disponible"
     } else { if (U \== []) {
         Severity = "ELEVEE";
         Reason   = "Alarme critique sans plan de reparation connu";
         Action   = "Contacter l equipe support pour diagnostic manuel"
     } else { if (A \== []) {
         Severity = "NORMALE";
         Reason   = "Alarme detectee, reparation planifiee";
         Action   = "Appliquer le plan de reparation"
     } else {
         Severity = "OK";
         Reason   = "Aucune anomalie detectee";
         Action   = "Aucune action requise"
     }}}}.

+!write_report(Severity, Reason, Action)
  <- ?report_file(File);
     ?critical_alarms(A);
     ?propagations(P);
     ?unhandled_alarms(U);
     .term2string(A, SA);
     .term2string(P, SP);
     .term2string(U, SU);
     .concat("SEVERITE : ", Severity, L1);
     .concat(L1, "\nRAISON   : ", L2);
     .concat(L2, Reason, L3);
     .concat(L3, "\nACTION   : ", L4);
     .concat(L4, Action, L5);
     .concat(L5, "\n\nAlarmes critiques:\n", L6);
     .concat(L6, SA, L7);
     .concat(L7, "\n\nPropagations:\n", L8);
     .concat(L8, SP, L9);
     .concat(L9, "\n\nAlarmes sans reparation:\n", L10);
     .concat(L10, SU, Report);
     joinWorkspace("sparql_workspace", WspId);
     lookupArtifact("sparql_manager", ArtId);
     focus(ArtId);
     writeReport(File, Report);
     .print("Coordinator: rapport ecrit dans ", File).
{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
