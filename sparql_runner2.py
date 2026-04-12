import requests
import json
import sys

ENDPOINT = "http://localhost:8890/sparql"

# ← Ta nouvelle requête ici
QUERY = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX noria:   <https://w3id.org/noria/ontology/>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?resource ?logMessage
WHERE {
  <https://w3id.org/noria/document/TT_TOY2022TT> dcterms:relation ?log .
  ?log noria:alarmPerceivedSeverity ?severity .
  FILTER (?severity = <https://w3id.org/noria/kos/Notification/Severity/PerceivedSeverity/minor>)
  ?log noria:logText ?logMessage .
  ?log noria:logOriginatingManagedObject ?resource .
}
"""

OUTPUT_FILE = "sparql_result2.json"    # ← fichier différent !

def run_query():
    print(f"[Python] Querying endpoint: {ENDPOINT}")
    headers = {"Accept": "application/sparql-results+json"}
    params  = {"query": QUERY, "format": "application/sparql-results+json"}
    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", {}).get("bindings", [])
        print(f"[Python] {len(results)} result(s) found.")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"[Python] Results written to '{OUTPUT_FILE}'.")
    except Exception as e:
        print(f"[Python] ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_query()