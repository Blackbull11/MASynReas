"""
High Impact Resource Detector - Structural / A Posteriori

Purpose
-------
This level-1 executor agent detects incident-affected resources that have
many structural dependencies in the NORIA-O knowledge graph.

Business intuition
------------------
A resource with high structural centrality is connected to many other
components, directly or indirectly, through dependency, support, containment,
or interface relationships.

If such a resource is involved in an incident, the potential impact radius
may be large. This may indicate:
- a broad blast radius,
- a critical structural bottleneck,
- a concentration of technical dependencies,
- or the need to prioritize incident handling and escalation.

Interest of the query
---------------------
This is a structural a posteriori diagnostic check focused on incident-related
resources.

Its goal is not only to identify the impacted resource itself, but also to
estimate whether the resource sits in a high-impact structural position in the
graph. This is useful for prioritization, incident triage, and root-cause
analysis, especially when the affected component supports many dependent
elements.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- No Redundancy Incident Detector,
- Child Component Incident Escalation Detector,
- Application Mapping Inconsistency Detector,
- Structural Dependency Expansion,
- Criticality vs Structural Weakness Detector.

Output
------
Results are written to:
results/structural/aposteriori/high_impact_resource_results.json
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
       (COUNT(DISTINCT ?dependentResource) AS ?dependentResourceCount)
       (COUNT(DISTINCT ?dependentApplication) AS ?dependentApplicationCount)
WHERE {
  ?ticket a noria:TroubleTicket .
  ?ticket noria:troubleTicketImpacts ?resource .
  ?resource a noria:Resource .

  OPTIONAL {
    ?dependentResource noria:partOf ?resource .
    ?dependentResource a noria:Resource .
  }

  OPTIONAL {
    ?resource noria:resourceForApplication ?dependentApplication .
    ?dependentApplication a noria:Application .
  }
}
GROUP BY ?ticket ?resource
HAVING (
  (COUNT(DISTINCT ?dependentResource) + COUNT(DISTINCT ?dependentApplication)) >= 3
)
ORDER BY DESC(?dependentResourceCount) DESC(?dependentApplicationCount) ?ticket ?resource
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "structural"
    / "aposteriori"
    / "high_impact_resource_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[HighImpactResourceDetector] Querying endpoint: {ENDPOINT}")

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
            f"[HighImpactResourceDetector] "
            f"{len(results)} high-impact incident resource(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[HighImpactResourceDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[HighImpactResourceDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[HighImpactResourceDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[HighImpactResourceDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()