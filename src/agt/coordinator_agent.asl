workers_expected(3).
workers_done(0).
critical_alarms([]).
propagations([]).
unhandled_alarms([]).
report_file("diagnostic_noria.txt").

!wait_for_results.

+!wait_for_results
  <- .print("=== Coordinator: en attente des 3 workers... ===").

/* garde : ignorer les doublons par worker */
+worker_done("critical_alarm_agent", Result)[source(Sender)]
    : not received_critical
  <- +received_critical;
     .print("Coordinator: alarmes critiques recues");
     -+critical_alarms(Result);
     !increment_counter.

+worker_done("critical_alarm_agent", Result)[source(Sender)]
    : received_critical <- true.

+worker_done("propagation_agent", Result)[source(Sender)]
    : not received_propagation
  <- +received_propagation;
     .print("Coordinator: propagations recues");
     -+propagations(Result);
     !increment_counter.

+worker_done("propagation_agent", Result)[source(Sender)]
    : received_propagation <- true.

+worker_done("unhandled_agent", Result)[source(Sender)]
    : not received_unhandled
  <- +received_unhandled;
     .print("Coordinator: alarmes non traitees recues");
     -+unhandled_alarms(Result);
     !increment_counter.

+worker_done("unhandled_agent", Result)[source(Sender)]
    : received_unhandled <- true.

+worker_error(Id, Msg)[source(Sender)]
  <- .print("Coordinator: ERREUR du worker ", Id, " : ", Msg);
     !increment_counter.

/* garde : ne lancer le diagnostic qu'une seule fois */
+!increment_counter : not diagnosis_done
  <- ?workers_done(N);
     N1 = N + 1;
     -+workers_done(N1);
     ?workers_expected(Total);
     if (N1 >= Total) {
         +diagnosis_done;
         !run_diagnosis
     }.

+!increment_counter : diagnosis_done <- true.

+!run_diagnosis
  <- !compute_severity(Severity, Reason, Action);
     !write_report(Severity, Reason, Action);
     .print("");
     .print("=== DIAGNOSTIC GLOBAL NORIA ===");
     .print("Severite : ", Severity);
     .print("Raison   : ", Reason);
     .print("Action   : ", Action);
     .print("Rapport  : diagnostic_noria.txt");
     .print("================================").

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