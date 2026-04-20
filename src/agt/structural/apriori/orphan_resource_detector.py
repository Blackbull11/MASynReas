"""
Orphan Resource Detector - Structural / A Priori

Purpose
-------
This level-1 executor agent runs a SPARQL query on the NORIA-O knowledge graph
to detect orphan resources.

A resource is considered orphan when it exists in the graph but is not linked
to the main structural entities that would make it operationally meaningful,
such as:
- a network interface,
- an application,
- a management unit,
- a parent resource,
- or a child resource.

Business intuition
------------------
In an ICT network knowledge graph, a valid resource should generally belong to
a minimal technical structure. If a resource is isolated from the rest of the
graph, this may reveal:
- incomplete inventory ingestion,
- synchronization issues,
- stale objects,
- or structural modeling inconsistencies.

Interest of the query
---------------------
This is a fundamental structural sanity check. It is useful in a priori
analysis to identify weak points in the graph before any incident occurs.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger more specific agents such as:
- Missing Interface Detector,
- Application Mapping Verification,
- Resource Management Assignment Check,
- Resource Hierarchy Consistency Check,
- Data Ingestion Consistency Check.

Output
------
The SPARQL results are written to:
results/structural/apriori/orphan_resource_results.json
"""

import json
import sys
from pathlib import Path

import requests

# ============================================================
# USER-EDITABLE SECTION
# ============================================================

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX seas:  <https://w3id.org/seas/>

SELECT ?resource
WHERE {
  ?resource a noria:Resource .

  FILTER NOT EXISTS {
    ?interface a noria:NetworkInterface ;
               noria:networkInterfaceOf ?resource .
  }

  FILTER NOT EXISTS { ?resource noria:resourceForApplication ?app . }

  FILTER NOT EXISTS { ?resource noria:resourceManagedBy ?orgUnit . }

  FILTER NOT EXISTS { ?resource seas:subSystemOf ?parent . }
  FILTER NOT EXISTS { ?child seas:subSystemOf ?resource . }
}
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "structural" / "apriori" / "orphan_resource_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Run the SPARQL query and write the results to a JSON file."""
    print(f"[OrphanResourceDetector] Querying endpoint: {ENDPOINT}")

    headers = {"Accept": "application/sparql-results+json"}
    params = {
        "query": QUERY,
        "format": "application/sparql-results+json",
    }

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", {}).get("bindings", [])
        print(f"[OrphanResourceDetector] {len(results)} result(s) found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[OrphanResourceDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[OrphanResourceDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[OrphanResourceDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[OrphanResourceDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()
