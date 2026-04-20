"""
Orphan Interface Detector - Structural / A Priori

Purpose
-------
This level-1 executor agent detects network interfaces that are not attached
to any hosting resource in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, a network interface must belong to a physical or logical
resource (e.g., server, router, VNF). An interface without a hosting resource
is structurally invalid and usually indicates:
- incomplete or inconsistent data ingestion,
- deletion of a resource without cleaning its interfaces,
- or modeling errors in the graph construction.

Interest of the query
---------------------
This is a basic structural consistency check at the interface level.
It ensures that all interfaces are properly anchored in the infrastructure.

Detecting such anomalies improves the reliability of:
- topology reconstruction,
- connectivity reasoning,
- and downstream diagnostics.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Resource Recovery / Reconstruction Agent,
- Interface Cleanup / Validation Agent,
- Connectivity Consistency Check,
- Data Ingestion Consistency Check.

Output
------
Results are written to:
results/structural/apriori/orphan_interface_results.json
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

SELECT ?interface
WHERE {
  ?interface a noria:NetworkInterface .

  FILTER NOT EXISTS { ?interface noria:networkInterfaceOf ?resource . }
  FILTER NOT EXISTS { ?resource noria:networkInterfaceOf ?interface . }
}
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "structural" / "apriori" / "orphan_interface_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute SPARQL query and store results."""
    print(f"[OrphanInterfaceDetector] Querying endpoint: {ENDPOINT}")

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

        print(f"[OrphanInterfaceDetector] {len(results)} orphan interface(s) found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[OrphanInterfaceDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[OrphanInterfaceDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[OrphanInterfaceDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[OrphanInterfaceDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()