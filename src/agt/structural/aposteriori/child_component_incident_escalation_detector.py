"""
Child Component Incident Escalation Detector - Structural / A Posteriori

Purpose
-------
This level-1 executor agent detects incidents affecting child components whose
parent resource appears structurally critical in the NORIA-O knowledge graph.

Business intuition
------------------
An incident raised on a child component does not necessarily mean that the
root cause is local to that component. In many situations, the actual problem
may originate from a parent resource that hosts, contains, or structurally
supports the affected component.

If the parent resource is structurally critical, for example because it
supports several child resources or several applications, then the incident
should be escalated in the analysis to that parent level.

This pattern may indicate:
- a likely root cause located above the reported child component,
- a structurally important parent acting as a bottleneck,
- a larger potential impact radius than the ticket initially suggests,
- or the need to widen the diagnostic scope.

Interest of the query
---------------------
This is a structural a posteriori diagnostic check because it starts from an
incident context and uses the containment hierarchy to redirect attention
toward potentially more critical parent resources.

It is especially useful for root-cause analysis, because incidents reported on
subcomponents are often symptoms of a broader parent-level issue.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- High Impact Resource Detector,
- No Redundancy Incident Detector,
- Structural Dependency Expansion,
- Parent Resource Health Review,
- Incident Scope Escalation Analysis.

Output
------
Results are written to:
results/structural/aposteriori/child_component_incident_escalation_results.json
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
PREFIX dct:   <http://purl.org/dc/terms/>

SELECT ?ticket ?childResource ?parentResource
       (COUNT(DISTINCT ?siblingOrChild) AS ?childCount)
       (COUNT(DISTINCT ?supportedApplication) AS ?supportedApplicationCount)
WHERE {
  ?ticket a noria:TroubleTicket .
  ?ticket (noria:troubleTicketRelatedResource | (dct:relation/noria:logOriginatingManagedObject)) ?childResource .
  ?childResource a noria:Resource .
  ?childResource noria:partOf ?parentResource .
  ?parentResource a noria:Resource .

  OPTIONAL {
    ?siblingOrChild a noria:Resource .
    ?siblingOrChild noria:partOf ?parentResource .
  }

  OPTIONAL {
    ?parentResource noria:resourceForApplication ?supportedApplication .
    ?supportedApplication a noria:Application .
  }
}
GROUP BY ?ticket ?childResource ?parentResource
HAVING (
  COUNT(DISTINCT ?siblingOrChild) >= 2
  ||
  COUNT(DISTINCT ?supportedApplication) >= 1
)
ORDER BY DESC(?childCount) DESC(?supportedApplicationCount) ?ticket ?childResource ?parentResource
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "structural"
    / "aposteriori"
    / "child_component_incident_escalation_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ChildComponentIncidentEscalationDetector] Querying endpoint: {ENDPOINT}")

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
            f"[ChildComponentIncidentEscalationDetector] "
            f"{len(results)} child-component incident escalation pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[ChildComponentIncidentEscalationDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[ChildComponentIncidentEscalationDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[ChildComponentIncidentEscalationDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[ChildComponentIncidentEscalationDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()