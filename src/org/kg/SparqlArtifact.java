package org.kg;

import org.apache.jena.query.QueryExecution;
import org.apache.jena.query.QueryExecutionFactory;
import org.apache.jena.query.ResultSet;
import org.apache.jena.query.ResultSetFormatter;
import cartago.Artifact;
import cartago.OPERATION;

import java.io.*;
import java.nio.file.*;

public class SparqlArtifact extends Artifact {

    // ─────────────────────────────────────────────
    // OPERATION 1 — original Jena-based SPARQL query
    // (kept exactly as before)
    // ─────────────────────────────────────────────
    @OPERATION
    public void execQuery(String endpointUrl, String sparqlQuery) {
        log("Connexion à l'endpoint : " + endpointUrl);

        try {
            QueryExecution qexec = QueryExecutionFactory.sparqlService(endpointUrl, sparqlQuery);
            ResultSet results = qexec.execSelect();
            String resultText = ResultSetFormatter.asText(results);

            log("Requête réussie, envoi du signal...");
            signal("query_result", resultText);

            qexec.close();
        } catch (Exception e) {
            log("Erreur lors de la requête : " + e.getMessage());
            signal("query_error", "Exception Jena: " + e.getMessage());
        }
    }

    // ─────────────────────────────────────────────
    // OPERATION 2 — delegate to a user-defined Python script
    // The script handles its own logic (queries, actions, etc.)
    // Results are read back from a JSON file it writes
    // ─────────────────────────────────────────────
    @OPERATION
    public void execPython(String scriptPath, String resultFilePath) {
        log("Lancement du script Python : " + scriptPath);

        try {
            // 1. Run the Python script as a subprocess
            // AFTER
            String pythonCmd = System.getProperty("os.name").toLowerCase().contains("win") ? "python" : "python3";
            ProcessBuilder pb = new ProcessBuilder(pythonCmd, scriptPath);
            pb.redirectErrorStream(true);
            pb.directory(new File(System.getProperty("user.dir")));
            Process process = pb.start();

            // 2. Stream Python stdout to the JaCaMo console
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream())
            );
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
                log("[Python] " + line);
            }

            int exitCode = process.waitFor();

            // 3. Non-zero exit = script reported an error
            if (exitCode != 0) {
                signal("query_error",
                    "Script Python terminé avec le code " + exitCode + ":\n" + output);
                return;
            }

            // 4. Read the result file written by the Python script
            File resultFile = new File(resultFilePath);
            if (!resultFile.exists()) {
                signal("query_error",
                    "Fichier résultat introuvable : " + resultFilePath);
                return;
            }

            String result = new String(Files.readAllBytes(resultFile.toPath()));
            log("Script terminé avec succès, envoi du signal...");
            signal("query_result", result);

        } catch (Exception e) {
            log("Erreur lors de l'exécution Python : " + e.getMessage());
            signal("query_error", "Exception Java: " + e.getMessage());
        }
    }
}