"""
Missing Parent Resource Detector - Structural / A Priori

Purpose
-------
This level-1 executor agent detects resources that behave like subordinate
components in the infrastructure but do not have any structural parent in
the NORIA-O knowledge graph.

Dataset-specific alignment
--------------------------
In this toy dataset, structural hierarchy is expressed with:
- seas:subSystemOf

This corrected version uses a stricter and more conservative heuristic:
a suspicious resource is a resource that:
- has no structural parent,
- has no structural children,
- and participates in the operational graph.

This avoids flagging legitimate top-level containers such as racks.

Business intuition
------------------
Some resources are expected to belong to a larger structural entity.
If such a resource has no parent and is not itself a structural container,
this may indicate:
- broken containment modeling,
- incomplete hierarchy ingestion,
- missing hosting relationships,
- or structural inconsistency.

Interest of the query
---------------------
This query checks the integrity of the structural hierarchy while avoiding
false positives on legitimate root resources.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Orphan Resource Detector,
- Hosting Structure Reconstruction,
- Hierarchy Ingestion Validation,
- Resource Modeling Consistency Check.

Output
------
Results are written to:
results/structural/apriori/missing_parent_resource_results.json
"""

import json
import sys
from pathlib import Path

import requests

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX seas:  <https://w3id.org/seas/>

SELECT DISTINCT ?resource
WHERE {
  ?resource a noria:Resource .

  # No structural parent
  FILTER NOT EXISTS {
    ?resource seas:subSystemOf ?parent .
  }

  # Not a structural root/container
  FILTER NOT EXISTS {
    ?child seas:subSystemOf ?resource .
  }

  # Keep only operationally relevant resources
  {
    ?resource noria:resourceForApplication ?app .
  }
  UNION
  {
    ?resource noria:resourceManagedBy ?orgUnit .
  }
  UNION
  {
    ?link noria:networkLinkTerminationResource ?resource .
  }
}
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "structural" / "apriori" / "missing_parent_resource_results.json"


def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[MissingParentResourceDetector] Querying endpoint: {ENDPOINT}")

    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": QUERY, "format": "application/sparql-results+json"}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", {}).get("bindings", [])

        print(f"[MissingParentResourceDetector] {len(results)} resource(s) without structural parent found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[MissingParentResourceDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[MissingParentResourceDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[MissingParentResourceDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[MissingParentResourceDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()