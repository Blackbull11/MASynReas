"""
No Redundancy Incident Detector - Structural / A Posteriori

Purpose
-------
This level-1 executor agent detects incidents affecting resources for which
no visible redundancy or failover support is present in the NORIA-O knowledge
graph.

Business intuition
------------------
When an incident affects a resource that has no visible backup, alternate
component, or structural redundancy, the operational risk is higher.

Such a situation may indicate:
- a single point of failure,
- an infrastructure fragility,
- a lack of resilience in the technical design,
- or incomplete modeling of failover-related support in the knowledge graph.

Interest of the query
---------------------
This is a structural a posteriori diagnostic check. It focuses on resources
already involved in an incident and verifies whether the graph exposes any
visible redundancy around them.

This is important during incident diagnosis because the absence of visible
redundancy increases the urgency of the situation and may explain why the
incident has a strong service impact.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- High Impact Resource Detector,
- Isolated Incident Resource Detector,
- Criticality vs Structural Weakness Detector,
- Structural Resilience Review,
- Escalation Priority Assessment.

Output
------
Results are written to:
results/structural/aposteriori/no_redundancy_incident_results.json
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

SELECT ?ticket ?resource
WHERE {
  ?ticket a noria:TroubleTicket .
  ?ticket noria:troubleTicketImpacts ?resource .
  ?resource a noria:Resource .

  FILTER NOT EXISTS {
    ?otherResource a noria:Resource .
    ?otherResource noria:partOf ?parent .
    ?resource noria:partOf ?parent .
    FILTER(?otherResource != ?resource)
  }

  FILTER NOT EXISTS {
    ?interface a noria:NetworkInterface .
    ?interface noria:networkInterfaceOf ?resource .
    ?interface noria:networkInterfaceConnects ?link .

    ?otherInterface a noria:NetworkInterface .
    ?otherInterface noria:networkInterfaceConnects ?link .
    ?otherInterface noria:networkInterfaceOf ?otherResource .

    FILTER(?otherResource != ?resource)
  }
}
ORDER BY ?ticket ?resource
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "structural"
    / "aposteriori"
    / "no_redundancy_incident_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[NoRedundancyIncidentDetector] Querying endpoint: {ENDPOINT}")

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
            f"[NoRedundancyIncidentDetector] "
            f"{len(results)} incident resource(s) without visible redundancy found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[NoRedundancyIncidentDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[NoRedundancyIncidentDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[NoRedundancyIncidentDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[NoRedundancyIncidentDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()