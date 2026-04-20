"""
Incomplete Network Link Detector - Structural / A Priori

Purpose
-------
This level-1 executor agent detects network links that are structurally incomplete
in the NORIA-O knowledge graph.

Dataset-specific alignment
--------------------------
In this toy dataset, a network link reaches its endpoints through:
- noria:networkLinkTerminationResource

A network link is considered incomplete when it is linked to fewer than two
distinct termination resources.

Business intuition
------------------
A valid network link should connect at least two endpoints. If a link has
fewer than two distinct termination resources, this may indicate:
- incomplete topology ingestion,
- missing endpoint resources,
- partial graph construction,
- or a malformed communication path.

Interest of the query
---------------------
This is a core topology completeness check.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Unconnected Interface Detector,
- Missing Endpoint Resource Check,
- Topology Reconstruction Agent,
- Link/Interface Consistency Check.

Output
------
Results are written to:
results/structural/apriori/incomplete_network_link_results.json
"""

import json
import sys
from pathlib import Path

import requests

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>

SELECT ?link (COUNT(DISTINCT ?resource) AS ?endpointCount)
WHERE {
  ?link a noria:NetworkLink .
  OPTIONAL {
    ?link noria:networkLinkTerminationResource ?resource .
  }
}
GROUP BY ?link
HAVING (COUNT(DISTINCT ?resource) < 2)
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "structural" / "apriori" / "incomplete_network_link_results.json"


def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[IncompleteNetworkLinkDetector] Querying endpoint: {ENDPOINT}")

    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": QUERY, "format": "application/sparql-results+json"}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", {}).get("bindings", [])

        print(f"[IncompleteNetworkLinkDetector] {len(results)} incomplete network link(s) found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[IncompleteNetworkLinkDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[IncompleteNetworkLinkDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[IncompleteNetworkLinkDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[IncompleteNetworkLinkDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()