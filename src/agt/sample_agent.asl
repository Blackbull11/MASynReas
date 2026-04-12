/* ── beliefs ── */
endpoint("http://localhost:8890/sparql").
result_file("sparql_result.json").
python_script("sparql_runner.py").

mode(python).   // ← switch to mode(jena) to use the original Jena path

/* ── initial goal ── */
!start_query.

/* ── Plans ── */

// --- Python mode: delegate everything to the user's Python script ---
+!start_query : mode(python)
  <- .print("Agent: Mode Python — lancement du script utilisateur...");
     joinWorkspace("sparql_workspace", WspId);
     lookupArtifact("sparql_manager", ArtId);
     focus(ArtId);
     ?python_script(Script);
     ?result_file(ResultFile);
     execPython(Script, ResultFile).

// --- Jena mode: original direct SPARQL query ---
+!start_query : mode(jena)
  <- .print("Agent: Mode Jena — exécution de la requête SPARQL directe...");
     joinWorkspace("sparql_workspace", WspId);
     lookupArtifact("sparql_manager", ArtId);
     focus(ArtId);
     ?endpoint(E);
     ?query(Q);
     execQuery(E, Q).

// --- Fallback ---
+!start_query
  <- .print("Agent: ERREUR — mode inconnu ou plan échoué.").

/* ── Result handlers ── */
+query_result(Result)
  <- .print("--- Résultat ---");
     .print(Result);
     .print("----------------").

+query_error(ErrorMsg)
  <- .print("!!! ERREUR !!!");
     .print(ErrorMsg);
     .print("---------------").

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }