"""
Unconnected Interface Detector - Structural / A Priori

Purpose
-------
This level-1 executor agent detects network interfaces that are attached to a
resource but are not connected to any network link in the NORIA-O knowledge graph.

Dataset-specific alignment
--------------------------
In this toy dataset, interfaces are linked to resources through:
- noria:networkInterfaceOf

and linked to network links through:
- noria:networkInterfaceConnects

Business intuition
------------------
An interface attached to a resource but not connected to any link may indicate:
- incomplete topology modeling,
- a missing edge in the graph,
- an unused or misconfigured interface,
- or an ingestion inconsistency.

Interest of the query
---------------------
This is a local topology consistency check at the interface level.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Incomplete Network Link Detector,
- Hosting Resource Connectivity Check,
- Interface State Verification,
- Topology Completion Check.

Output
------
Results are written to:
results/structural/apriori/unconnected_interface_results.json
"""

import json
import sys
from pathlib import Path

import requests

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>

SELECT ?resource ?interface
WHERE {
  ?interface a noria:NetworkInterface ;
             noria:networkInterfaceOf ?resource .

  FILTER NOT EXISTS {
    ?interface noria:networkInterfaceConnects ?link .
  }
}
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "structural" / "apriori" / "unconnected_interface_results.json"


def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[UnconnectedInterfaceDetector] Querying endpoint: {ENDPOINT}")

    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": QUERY, "format": "application/sparql-results+json"}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", {}).get("bindings", [])

        print(f"[UnconnectedInterfaceDetector] {len(results)} unconnected interface(s) found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[UnconnectedInterfaceDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[UnconnectedInterfaceDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[UnconnectedInterfaceDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[UnconnectedInterfaceDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()