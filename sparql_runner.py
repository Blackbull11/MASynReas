import requests
import json
import sys

# ============================================================
#   USER-EDITABLE SECTION
#   Define your SPARQL endpoint and query here
# ============================================================

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX noria:   <https://w3id.org/noria/ontology/>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?resource ?logMessage ?repairLabel ?app
WHERE {
  <https://w3id.org/noria/document/TT_TOY2022TT> dcterms:relation ?log .
  ?log noria:alarmPerceivedSeverity ?severity .
  FILTER (?severity = <https://w3id.org/noria/kos/Notification/Severity/PerceivedSeverity/major>)
  ?log noria:logText ?logMessage .
  ?log noria:logOriginatingManagedObject ?resource .
  ?log noria:alarmProposedRepairAction ?repair .
  ?repair rdfs:label ?repairLabel .
  ?resource noria:resourceForApplication ?app .
}
"""

OUTPUT_FILE = "sparql_result.json"

# ============================================================
#   EXECUTION (do not modify below unless you know what you do)
# ============================================================

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

    except requests.exceptions.ConnectionError:
        print(f"[Python] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[Python] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[Python] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_query()