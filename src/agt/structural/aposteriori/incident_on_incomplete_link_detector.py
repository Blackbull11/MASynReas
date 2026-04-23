"""
Incident On Incomplete Link Detector - Structural / A Posteriori

Purpose
-------
This level-1 executor agent detects incidents involving resources that are
connected to incomplete or partially terminated network links in the NORIA-O
knowledge graph.

Business intuition
------------------
A network link should normally connect two valid endpoints through the
corresponding interfaces.

If an incident affects a resource that is attached to a link with only one
endpoint, or no proper termination at all, this may indicate:
- a broken or partially described topology,
- an actual connectivity weakness,
- an ingestion or modeling inconsistency in the graph,
- or a topology-related root cause contributing to the incident.

Interest of the query
---------------------
This is a structural a posteriori diagnostic check because it focuses on
resources already involved in an incident.

It is especially useful during diagnosis because incomplete links around an
impacted resource strongly suggest that the incident may be related to
topology defects, missing connection data, or structural fragility in the
network representation.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Isolated Incident Resource Detector,
- No Redundancy Incident Detector,
- Unconnected Interface Detector,
- Incomplete Network Link Detector,
- Resource Topology Consistency Check.

Output
------
Results are written to:
results/structural/aposteriori/incident_on_incomplete_link_results.json
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

SELECT DISTINCT ?ticket ?resource ?interface ?link (COUNT(DISTINCT ?endpointInterface) AS ?endpointCount)
WHERE {
  ?ticket a noria:TroubleTicket .
  ?ticket noria:troubleTicketImpacts ?resource .
  ?resource a noria:Resource .

  ?interface a noria:NetworkInterface .
  ?interface noria:networkInterfaceOf ?resource .
  ?interface noria:networkInterfaceConnects ?link .
  ?link a noria:NetworkLink .

  OPTIONAL {
    ?endpointInterface a noria:NetworkInterface .
    ?endpointInterface noria:networkInterfaceConnects ?link .
  }
}
GROUP BY ?ticket ?resource ?interface ?link
HAVING (COUNT(DISTINCT ?endpointInterface) <= 1)
ORDER BY ?ticket ?resource ?link
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "structural"
    / "aposteriori"
    / "incident_on_incomplete_link_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[IncidentOnIncompleteLinkDetector] Querying endpoint: {ENDPOINT}")

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
            f"[IncidentOnIncompleteLinkDetector] "
            f"{len(results)} incident-related incomplete link pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[IncidentOnIncompleteLinkDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[IncidentOnIncompleteLinkDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[IncidentOnIncompleteLinkDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[IncidentOnIncompleteLinkDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()