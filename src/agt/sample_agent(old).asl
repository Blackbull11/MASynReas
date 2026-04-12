// Agent bob in project appSPARQL
/* Initial beliefs and rules */
endpoint("http://localhost:8890/sparql").

query("PREFIX dcterms: <http://purl.org/dc/terms/> PREFIX noria: <https://w3id.org/noria/ontology/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?resource ?logMessage ?repairLabel ?app  WHERE { <https://w3id.org/noria/document/TT_TOY2022TT> dcterms:relation ?log . ?log noria:alarmPerceivedSeverity ?severity . FILTER (?severity = <https://w3id.org/noria/kos/Notification/Severity/PerceivedSeverity/major>) ?log noria:logText ?logMessage . ?log noria:logOriginatingManagedObject ?resource . ?log noria:alarmProposedRepairAction ?repair . ?repair rdfs:label ?repairLabel . ?resource noria:resourceForApplication ?app . }").

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
 <- .print("Agent: !!! ERREUR FATALE - Le plan principal aéchoué !!!");
 .print("Agent: L'opération sparql_manager.execQuery aéchoué.").


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
