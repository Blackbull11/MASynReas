"""
Application Mapping Inconsistency Detector - Structural / A Posteriori

Purpose
-------
This level-1 executor agent detects incidents involving applications whose
technical support mapping is incomplete or ambiguous in the NORIA-O knowledge
graph.

Business intuition
------------------
When an application is involved in an incident, its supporting technical
resources should be clearly identifiable in the knowledge graph.

If an incident-related application has no visible supporting resource, or if
its support mapping is fragmented across several unrelated resources, this may
indicate:
- an incomplete structure-function mapping,
- ambiguous technical ownership,
- missing deployment information,
- or a graph representation that can mislead incident diagnosis.

Interest of the query
---------------------
This is a structural a posteriori diagnostic check because it focuses on
applications already involved in an incident context.

It is particularly useful during diagnosis, since unclear infrastructure
support makes it difficult to identify the real technical root cause, route
the issue correctly, or estimate the operational scope of the incident.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Application Without Infrastructure Support Detector,
- High Impact Resource Detector,
- Child Component Incident Escalation Detector,
- Technical Support Mapping Review,
- Incident Routing Consistency Check.

Output
------
Results are written to:
results/structural/aposteriori/application_mapping_inconsistency_results.json
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

SELECT ?ticket ?application
       (COUNT(DISTINCT ?supportResource) AS ?supportResourceCount)
       (COUNT(DISTINCT ?parentResource) AS ?parentSupportGroupCount)
WHERE {
  ?ticket a noria:TroubleTicket .
  ?ticket noria:troubleTicketImpacts ?application .
  ?application a noria:Application .

  OPTIONAL {
    ?supportResource noria:resourceForApplication ?application .
    ?supportResource a noria:Resource .

    OPTIONAL {
      ?supportResource noria:partOf ?parentResource .
      ?parentResource a noria:Resource .
    }
  }
}
GROUP BY ?ticket ?application
HAVING (
  COUNT(DISTINCT ?supportResource) = 0
  ||
  (
    COUNT(DISTINCT ?supportResource) > 1
    &&
    COUNT(DISTINCT ?parentResource) > 1
  )
)
ORDER BY ?ticket ?application
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "structural"
    / "aposteriori"
    / "application_mapping_inconsistency_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ApplicationMappingInconsistencyDetector] Querying endpoint: {ENDPOINT}")

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
            f"[ApplicationMappingInconsistencyDetector] "
            f"{len(results)} incident-related application mapping inconsistency pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[ApplicationMappingInconsistencyDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[ApplicationMappingInconsistencyDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[ApplicationMappingInconsistencyDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[ApplicationMappingInconsistencyDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()