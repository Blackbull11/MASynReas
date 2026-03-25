// Agent bob in project appSPARQL

/* Initial beliefs and rules */
endpoint("http://localhost:8890/sparql").
query("SELECT DISTINCT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10").

/* Initial goals */

!start_query.

/* Plans */

+!start_query
    <- .print("Agent: Exécution de la requête sur localhost:8890/sparql...");
       joinWorkspace("sparql_workspace", WspId);
       lookupArtifact("sparql_manager", ArtId);
       focus(ArtId);
       .findall(Qry, query(Qry), Queries);
       Queries = [Q|_];
       ?endpoint(E);
       execQuery(E, Q).

+!start_query : .fail
    <- .print("Agent: !!! ERREUR FATALE - Le plan principal a échoué !!!");
       .print("Agent: L'opération sparql_manager.execQuery a échoué.").

+query_result(Result)
    <- .print("--- Résultat de la requête SPARQL ---");
       .print(Result);
       .print("-------------------------------------").

+query_error(ErrorMsg)
    <- .print("!!! ERREUR SPARQL !!!") ;
       .print(ErrorMsg);
       .print("-----------------------").


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moise/asl/org-obedient.asl") }
