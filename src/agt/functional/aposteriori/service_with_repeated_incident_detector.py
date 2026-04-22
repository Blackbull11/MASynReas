"""
Service With Repeated Incident Detector - Functional / A Posteriori

Purpose
-------
This level-1 executor agent detects services that are impacted repeatedly by
technical events through the functional support chain in the NORIA-O
knowledge graph.

Business intuition
------------------
In an ICT network, a service that is repeatedly associated with incidents is
often a sign of chronic fragility, unresolved underlying issues, recurrent
resource instability, or insufficient remediation after previous faults.

Even if each low-level event appears isolated, their repeated convergence
towards the same service is highly relevant for diagnosis.

Interest of the query
---------------------
This detector helps identify services that are repeatedly impacted by events
originating from their supporting resources.

It is useful for:
- detecting chronic service instability,
- prioritizing recurring issues,
- supporting root cause analysis,
- and identifying services requiring structural remediation.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Chronic Service Fragility Analysis,
- Root Cause Recurrence Check,
- Repeated Resource Correlation Analysis,
- Service Criticality Reassessment,
- Incident Escalation Recommendation.

Output
------
Results are written to:
results/functional/aposteriori/service_with_repeated_incident_results.json
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

SELECT ?service (COUNT(DISTINCT ?event) AS ?eventCount)
WHERE {
  ?event a noria:EventRecord ;
         noria:logOriginatingManagedObject ?resource .

  ?resource noria:resourceForApplication ?application .

  ?module a noria:ApplicationModule ;
          noria:applicationModuleOf ?application ;
          seas:subSystemOf ?service .

  ?service a noria:Service .
}
GROUP BY ?service
HAVING (COUNT(DISTINCT ?event) > 1)
ORDER BY DESC(?eventCount) ?service
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "functional" / "aposteriori" / "service_with_repeated_incident_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ServiceWithRepeatedIncidentDetector] Querying endpoint: {ENDPOINT}")

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
            "[ServiceWithRepeatedIncidentDetector] "
            f"{len(results)} service(s) with repeated incidents found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[ServiceWithRepeatedIncidentDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[ServiceWithRepeatedIncidentDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[ServiceWithRepeatedIncidentDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[ServiceWithRepeatedIncidentDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()