"""
Change Linked To Multiple Incidents Detector - Procedural / A Posteriori

Purpose
-------
This level-1 executor agent detects ChangeRequest instances that are linked
to multiple TroubleTicket incidents in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, a change request is expected to modify part of the system
in a controlled and localized way. If a single change is associated with
several incident tickets, this may indicate:
- a high-impact or badly prepared change,
- a faulty deployment or rollback process,
- a broad operational disturbance caused by the same intervention,
- or an overly coarse correlation between change management and incident management.

Interest of the query
---------------------
This is a key procedural consistency and impact analysis check between the
change management layer and the incident management layer.

It is especially useful in a posteriori analysis because it highlights
changes that appear to have generated or been associated with several
distinct incidents. Such changes deserve prioritization in postmortem,
risk review, and process improvement workflows.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Post-Change Validation Check,
- Change Blast Radius Analysis,
- Repeated Incident Correlation Check,
- Root Cause Consolidation Analysis,
- Change Governance Review.

Output
------
Results are written to:
results/procedural/aposteriori/change_linked_to_multiple_incidents_results.json
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
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?change (COUNT(DISTINCT ?ticket) AS ?incidentCount)
WHERE {
  ?change a noria:ChangeRequest .
  ?ticket a noria:TroubleTicket .

  {
    ?change dcterms:relation ?ticket .
  }
  UNION
  {
    ?ticket dcterms:relation ?change .
  }
}
GROUP BY ?change
HAVING (COUNT(DISTINCT ?ticket) > 1)
ORDER BY DESC(?incidentCount)
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "procedural" / "aposteriori" / "change_linked_to_multiple_incidents_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ChangeLinkedToMultipleIncidentsDetector] Querying endpoint: {ENDPOINT}")

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

        print(f"[ChangeLinkedToMultipleIncidentsDetector] {len(results)} change request(s) linked to multiple incidents found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[ChangeLinkedToMultipleIncidentsDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[ChangeLinkedToMultipleIncidentsDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[ChangeLinkedToMultipleIncidentsDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[ChangeLinkedToMultipleIncidentsDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()