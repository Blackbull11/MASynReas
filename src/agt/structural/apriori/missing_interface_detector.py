"""
Missing Network Interface Detector - Structural / A Priori

Purpose
-------
This level-1 executor agent detects resources that do not expose any explicit
network interface in the NORIA-O knowledge graph.

Dataset-specific note
---------------------
In this toy dataset, many topological relations are modeled directly through
network links and termination resources, and only a subset of resources expose
explicit NetworkInterface instances.

Therefore, this detector is intentionally strict:
it only checks the absence of explicit interfaces linked through
noria:networkInterfaceOf.

Business intuition
------------------
A resource without any explicit network interface may indicate:
- incomplete topology modeling,
- partial inventory ingestion,
- missing interface-level data,
- or an intentionally simplified representation.

Interest of the query
---------------------
This query is useful to identify resources for which interface-level modeling
is absent. On this toy dataset, the detector should be interpreted as a
"description completeness" check rather than as a proof of actual isolation.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Unconnected Interface Detector,
- Incomplete Network Link Detector,
- Resource Modeling Completeness Check,
- Topology Ingestion Consistency Check.

Output
------
Results are written to:
results/structural/apriori/missing_interface_results.json
"""

import json
import sys
from pathlib import Path

import requests

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>

SELECT ?resource
WHERE {
  ?resource a noria:Resource .

  FILTER NOT EXISTS {
    ?interface a noria:NetworkInterface ;
               noria:networkInterfaceOf ?resource .
  }
}
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "structural" / "apriori" / "missing_interface_results.json"


def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[MissingInterfaceDetector] Querying endpoint: {ENDPOINT}")

    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": QUERY, "format": "application/sparql-results+json"}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", {}).get("bindings", [])

        print(f"[MissingInterfaceDetector] {len(results)} resource(s) without explicit interface found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[MissingInterfaceDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[MissingInterfaceDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[MissingInterfaceDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[MissingInterfaceDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()