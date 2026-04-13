/* ── beliefs ── */
result_file("sparql_result2.json").      // ← fichier différent !
python_script("sparql_runner2.py").      // ← script différent !

mode(python).

/* ── initial goal ── */
!start_query.

/* ── Plans ── (identiques à sample_agent.asl) ── */

+!start_query : mode(python)
  <- .print("Agent2: Lancement du script utilisateur...");
     joinWorkspace("sparql_workspace", WspId);
     lookupArtifact("sparql_manager", ArtId);
     focus(ArtId);
     ?python_script(Script);
     ?result_file(ResultFile);
     execPython(Script, ResultFile).

+!start_query
  <- .print("Agent2: ERREUR — plan échoué.").

+query_result(Result)
  <- .print("--- Résultat Agent2 ---");
     .print(Result);
     .print("----------------------").

+query_error(ErrorMsg)
  <- .print("!!! ERREUR Agent2 !!!");
     .print(ErrorMsg);
     .print("--------------------").

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }