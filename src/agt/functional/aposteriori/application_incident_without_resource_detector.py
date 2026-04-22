"""
Application Incident Without Resource Detector - Functional / A Posteriori

Purpose
-------
This level-1 executor agent detects application-level incidents or event records
whose originating management system is an application that is not linked to any
supporting resource in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, an application that appears as the source of an operational
event should normally be anchored to at least one technical resource such as a
server, VM, network function, or other infrastructure component.

If an event is emitted by an application that has no associated resource, this
may indicate:
- incomplete mapping between functional and technical layers,
- missing deployment information,
- incomplete ingestion of infrastructure dependencies,
- or a monitoring view that references an application not grounded in the
  actual network.

Interest of the query
---------------------
This is a functional consistency check used in a posteriori analysis.

It is useful because it highlights incidents that appear at the application
layer but cannot be traced back to any supporting technical resource. In such
a situation, diagnosis and root-cause analysis may become incomplete or
misleading, since the functional symptom has no visible infrastructure anchor.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Application Deployment Consistency Check,
- Functional-to-Technical Mapping Verification,
- Incident Traceability Check,
- Orphan Application Investigation,
- Data Ingestion Consistency Check.

Output
------
Results are written to:
results/functional/aposteriori/application_incident_without_resource_results.json
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

SELECT ?event ?application ?time ?type
WHERE {
  ?event a noria:EventRecord ;
         noria:logOriginatingManagementSystem ?application ;
         noria:loggingTime ?time .

  ?application a noria:Application .

  OPTIONAL { ?event <http://purl.org/dc/terms/type> ?type . }

  FILTER NOT EXISTS {
    ?resource noria:resourceForApplication ?application .
  }
}
ORDER BY ?time
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "functional" / "aposteriori" / "application_incident_without_resource_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ApplicationIncidentWithoutResourceDetector] Querying endpoint: {ENDPOINT}")

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
            "[ApplicationIncidentWithoutResourceDetector] "
            f"{len(results)} application incident(s) without support resource found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[ApplicationIncidentWithoutResourceDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[ApplicationIncidentWithoutResourceDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[ApplicationIncidentWithoutResourceDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[ApplicationIncidentWithoutResourceDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()