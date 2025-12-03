// Agent `bob` — exemple complet recevant un `Map` depuis l'artefact SPARQL

/*
  Comportement:
  - !start : initialise l'agent
  - +!find_info(Theme) : construit une requête SPARQL et demande à l'artefact `kg`
  - +query_result(ResultMap) : reçoit un java.util.Map<String,String> pour un binding
  - +query_error(Msg) : reçoit les erreurs éventuelles

  Remarques:
  - L'artefact doit émettre: signal("query_result", map);
    où `map` est un `java.util.Map` contenant var->value (par ex. "s"->"http://...", "p"->"..." )
  - Si vous préférez des signaux avec des arguments séparés, adaptez les plans `+query_result(...)` en conséquence.
*/

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }

!start.

/* petit démarrage */
+!start : true
    <- .print("Agent bob démarré.");
       .date(Y,M,D); .time(H,Min,Sec,MilSec);
       +started(Y,M,D,H,Min,Sec).


/*
  Plan pour lancer la requête SPARQL vers l'artefact `kg`.
  - `Theme` est une chaîne passée en paramètre au goal.
  - Ici on montre une requête simple; adaptez la chaîne SPARQL selon vos besoins.
*/

@plan
+!find_info(Theme)
   <-
      // Exemple minimal de requête qui utilise la variable Theme dans un filtre (adapter selon endpoint).
      // Pour éviter les complexités de concaténation, on construit une requête simple ici.
      SparqlQuery = "SELECT ?s ?p WHERE { ?s ?p ?o . FILTER(CONTAINS(LCASE(STR(?o)), '" + Theme + "')) } LIMIT 10";

      // Appel asynchrone à l'opération `query` de l'artefact `kg` (déclaré dans my_app.jcm)
      query(SparqlQuery)[artifact_name(kg)];

      .print("Requête envoyée au KG : ", SparqlQuery).


/*
  Plan pour traiter chaque résultat envoyé par l'artefact.
  L'artefact envoie un objet Java `Map<String,String>` (ResultMap).
  On récupère les variables connues (ex: "s", "p") via ResultMap.get("s").
*/

@plan
+query_result(ResultMap)
   <- .print("Signal 'query_result' reçu (raw): ", ResultMap);
      // Exemples d'accès: adaptez les clés aux noms de variables SPARQL (sans le '?')
      try {
         S = ResultMap.get("s");
      } catch (Exception e) {
         S = "<n/a>";
      }
      try {
         P = ResultMap.get("p");
      } catch (Exception e) {
         P = "<n/a>";
      }

      .print("  s = ", S, "\n  p = ", P).


/* Gestion d'erreur envoyée par l'artefact */
@plan
+query_error(Msg)
   <- .print("Erreur depuis l'artefact SPARQL: ", Msg).


/* Optionnel: si l'artefact peut envoyer les résultats ligne-par-ligne
   chaque signal contenant un Map (une ligne). Si l'artefact envoie une
   liste/structure différente, adaptez ce plan. */
