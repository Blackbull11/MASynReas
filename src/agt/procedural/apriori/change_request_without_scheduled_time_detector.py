"""
Change Request Without Scheduled Time Detector - Procedural / A Priori

Purpose
-------
This level-1 executor agent detects ChangeRequest instances that do not
have any scheduled execution time in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, a change request should normally be planned within a
specific time window (start time, end time, or scheduled date). This allows
operators to:
- anticipate impact,
- coordinate interventions,
- avoid peak usage periods,
- and ensure proper rollback strategies if needed.

If a ChangeRequest exists without any associated scheduling information,
this may indicate:
- incomplete change planning,
- missing operational constraints,
- weak coordination between teams,
- or incomplete ingestion of change management data.

Interest of the query
---------------------
This is a core procedural preparedness check within the change management layer.

It is especially useful in a priori analysis because it identifies changes
that are not properly scheduled before execution. Such changes are more
likely to cause unexpected disruptions and complicate incident correlation.

Operational modeling choice
---------------------------
In this detector, a "scheduled time" is operationalized through the absence
of any temporal property attached to the ChangeRequest, such as:
- noria:plannedStartDate
- noria:plannedEndDate
- noria:changeDate
(or equivalent temporal predicates in the dataset)

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Change Planning Completeness Check,
- Change Risk Assessment,
- Missing Maintenance Window Detector,
- Change Coordination Analysis,
- Post-Change Incident Correlation.

Output
------
Results are written to:
results/procedural/apriori/change_request_without_scheduled_time_results.json
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

SELECT ?change ?status
WHERE {
  ?change a noria:ChangeRequest .

  OPTIONAL { ?change noria:changeStatus ?status . }

  FILTER NOT EXISTS { ?change noria:plannedStartDate ?start . }
  FILTER NOT EXISTS { ?change noria:plannedEndDate ?end . }
  FILTER NOT EXISTS { ?change noria:changeDate ?date . }
}
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "procedural" / "apriori" / "change_request_without_scheduled_time_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ChangeRequestWithoutScheduledTimeDetector] Querying endpoint: {ENDPOINT}")

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

        print(f"[ChangeRequestWithoutScheduledTimeDetector] {len(results)} change request(s) without scheduled time found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[ChangeRequestWithoutScheduledTimeDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[ChangeRequestWithoutScheduledTimeDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[ChangeRequestWithoutScheduledTimeDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[ChangeRequestWithoutScheduledTimeDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()