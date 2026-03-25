package org.kg;

import org.apache.jena.query.QueryExecution;
import org.apache.jena.query.QueryExecutionFactory;
import org.apache.jena.query.ResultSet;
import org.apache.jena.query.ResultSetFormatter;

import cartago.Artifact;
import cartago.OPERATION;

public class SparqlArtifact extends Artifact {

    @OPERATION
    public void execQuery(String endpointUrl, String sparqlQuery) {
        log("Connexion à l'endpoint : " + endpointUrl);
        
        try {
            // 1. Création de l'exécution SPARQL via Jena
            // Note: QueryExecutionFactory.sparqlService gère les requêtes HTTP vers l'endpoint
            QueryExecution qexec = QueryExecutionFactory.sparqlService(endpointUrl, sparqlQuery);
            
            // 2. Exécution de la requête SELECT
            ResultSet results = qexec.execSelect();
            
            // 3. Formatage du résultat en String (pour l'affichage console de l'agent)
            // Vous pourrez plus tard changer cela pour du JSON ou une structure Java
            String resultText = ResultSetFormatter.asText(results);
            
            log("Requête réussie, envoi du signal...");
            
            // 4. Envoi du résultat à l'agent
            signal("query_result", resultText);
            
            // 5. Fermeture de la connexion
            qexec.close();

        } catch (Exception e) {
            // En cas d'erreur (serveur éteint, syntaxe SPARQL incorrecte...)
            log("Erreur lors de la requête : " + e.getMessage());
            signal("query_error", "Exception Jena: " + e.getMessage());
        }
    }
}