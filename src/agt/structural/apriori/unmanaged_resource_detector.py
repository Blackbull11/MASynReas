"""
Unmanaged Resource Detector - Structural / A Priori

Purpose
-------
This level-1 executor agent detects resources that are not assigned to any
management unit in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, every operational resource should normally be associated
with a management entity, operational unit, or support team.

A resource without any management assignment may indicate:
- incomplete governance modeling,
- missing operational ownership,
- data ingestion issues,
- or weak supportability in case of incident escalation.

Interest of the query
---------------------
This is a structural and operational consistency check.

It is especially useful in a priori analysis because it reveals resources
that may become difficult to supervise, maintain, escalate, or diagnose
during real incidents.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Organizational Mapping Verification,
- Incident Routing Risk Assessment,
- Resource Criticality Review,
- Orphan Resource Detector,
- Data Ingestion Consistency Check.

Output
------
Results are written to:
results/structural/apriori/unmanaged_resource_results.json
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
PREFIX org:   <http://www.w3.org/ns/org#>

SELECT ?resource
WHERE {
  ?resource a noria:Resource .

  FILTER NOT EXISTS { ?resource noria:resourceManagedBy ?orgUnit . }
}
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "structural" / "apriori" / "unmanaged_resource_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[UnmanagedResourceDetector] Querying endpoint: {ENDPOINT}")

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

        print(f"[UnmanagedResourceDetector] {len(results)} unmanaged resource(s) found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[UnmanagedResourceDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[UnmanagedResourceDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[UnmanagedResourceDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[UnmanagedResourceDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()