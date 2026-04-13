!start_query.

+!start_query
  <- ?worker_id(Id);
     ?python_script(Script);
     ?result_file(ResultFile);
     .print("Worker ", Id, ": lancement de ", Script);
     joinWorkspace("sparql_workspace", WspId);
     lookupArtifact("sparql_manager", ArtId);
     focus(ArtId);
     execPython(Script, ResultFile).

/* garde : n'envoyer qu'une seule fois */
+query_result(Result) : not already_sent
  <- +already_sent;
     ?worker_id(Id);
     .print("Worker ", Id, ": resultat recu, envoi au coordinator...");
     .send(coordinator, tell, worker_done(Id, Result)).

+query_result(Result) : already_sent <- true.

+query_error(Msg) : not already_sent
  <- +already_sent;
     ?worker_id(Id);
     .print("Worker ", Id, ": ERREUR -> ", Msg);
     .send(coordinator, tell, worker_error(Id, Msg)).

+query_error(Msg) : already_sent <- true.

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }