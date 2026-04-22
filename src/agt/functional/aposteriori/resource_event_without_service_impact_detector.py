"""
Resource Event Without Service Impact Detector - Functional / A Posteriori

Purpose
-------
This level-1 executor agent detects events occurring on resources that cannot
be propagated to any service through the functional support chain in the
NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, a technical event occurring on a resource should normally
propagate to at least one service through the following chain:

resource → application → application module → service

If no such service can be reached, this may indicate:
- a local technical issue with no service impact,
- incomplete functional mapping,
- missing application-module relationships,
- or gaps in the knowledge graph.

Interest of the query
---------------------
This detector helps identify events that are "functionally isolated".

It is useful for:
- detecting blind spots in the functional model,
- identifying non-impacting infrastructure alerts,
- improving graph completeness,
- and avoiding misleading service-level diagnostics.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Functional Mapping Verification,
- Resource-to-Service Chain Completion Check,
- Orphan Resource Investigation,
- Impact Propagation Validation,
- Knowledge Graph Completeness Check.

Output
------
Results are written to:
results/functional/aposteriori/resource_event_without_service_impact_results.json
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
PREFIX seas: <https://w3id.org/seas/>

SELECT ?event ?time ?resource
WHERE {
  ?event a noria:EventRecord ;
         noria:loggingTime ?time ;
         noria:logOriginatingManagedObject ?resource .

  # The event is on a resource
  ?resource a noria:Resource .

  # Ensure NO service can be reached through functional chain
  FILTER NOT EXISTS {
    ?resource noria:resourceForApplication ?app .
    ?module noria:applicationModuleOf ?app .
    ?module seas:subSystemOf ?service .
  }
}
ORDER BY ?time ?event
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "functional" / "aposteriori" / "resource_event_without_service_impact_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ResourceEventWithoutServiceImpactDetector] Querying endpoint: {ENDPOINT}")

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

        print(
            "[ResourceEventWithoutServiceImpactDetector] "
            f"{len(results)} resource event(s) without service impact found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[ResourceEventWithoutServiceImpactDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[ResourceEventWithoutServiceImpactDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[ResourceEventWithoutServiceImpactDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[ResourceEventWithoutServiceImpactDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()