package kg;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.jena.query.Query;
import org.apache.jena.query.QueryExecution;
import org.apache.jena.query.QueryExecutionFactory;
import org.apache.jena.query.QueryFactory;
import org.apache.jena.query.QuerySolution;
import org.apache.jena.query.ResultSet;
import org.apache.jena.rdf.model.RDFNode;

import cartago.Artifact;
import cartago.OPERATION;

public class KGSparqlArtifact extends Artifact {

    private String endpointUrl = null;

    // init called when the artifact is created: pass endpoint URL as parameter if you want
    public void init(String endpointUrl) {
        this.endpointUrl = endpointUrl;
        // optionally create observable properties, logging, etc.
    }

    @OPERATION
    public void setEndpoint(String endpointUrl) {
        this.endpointUrl = endpointUrl;
    }

    @OPERATION
    public void query(String sparqlQuery) {
        if (sparqlQuery == null || sparqlQuery.trim().isEmpty()) {
            // nothing to do
            return;
        }

        Query query = QueryFactory.create(sparqlQuery);

        if (!query.isSelectType()) {
            // Only SELECT handled in this artifact
            signal("query_error", "Only SELECT queries supported");
            return;
        }

        try (QueryExecution qexec = createQueryExecution(query)) {
            ResultSet results = qexec.execSelect();
            List<String> vars = results.getResultVars();

            while (results.hasNext()) {
                QuerySolution sol = results.nextSolution();
                Map<String, String> map = new HashMap<>();

                for (String var : vars) {
                    RDFNode node = sol.get(var);
                    map.put(var, nodeToString(node));
                }

                // send the whole binding as one signal argument (agent receives a Map)
                signal("query_result", map);
            }
        } catch (Exception e) {
            signal("query_error", e.getMessage());
        }
    }

    // helper to create a QueryExecution: uses endpointUrl if set, otherwise throws
    private QueryExecution createQueryExecution(Query query) {
        if (endpointUrl != null && !endpointUrl.trim().isEmpty()) {
            return QueryExecutionFactory.sparqlService(endpointUrl, query);
        } else {
            throw new IllegalStateException("No SPARQL endpoint configured. Call init(endpointUrl) or setEndpoint(url).");
        }
    }

    private String nodeToString(RDFNode node) {
        if (node == null) return null;
        if (node.isLiteral()) return node.asLiteral().getString();
        if (node.isResource()) {
            String uri = node.asResource().getURI();
            return uri != null ? uri : node.toString();
        }
        return node.toString();
    }
}