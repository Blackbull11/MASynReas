"""
Change Overlap Conflict Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects patterns in the NORIA-O knowledge graph
where two ChangeRequest instances overlap in time on the same related element.

Business intuition
------------------
When two changes are executed at overlapping times on the same network element,
they may interfere with each other and create unstable or unexpected behavior.

Such a pattern may correspond to:
- concurrent operational actions on the same resource,
- conflicting configuration updates,
- maintenance actions executed without proper coordination,
- or an operational context that can explain a subsequent incident.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it exploits the
temporal organization of observed ChangeRequest instances to identify a
potentially conflicting operational situation.

It is particularly useful during diagnosis because it helps:
- orient the investigation toward operational causes,
- identify suspicious concurrent interventions,
- provide an explainable temporal conflict signal,
- and support higher-level reasoning about post-change anomalies.

Detection logic
---------------
For each pair of distinct ChangeRequest instances:
- both changes affect the same related element,
- both have an actual start time and an actual end time,
- and their real execution intervals overlap.

Two intervals [start1, end1] and [start2, end2] are considered overlapping if:
- start1 <= end2
- and start2 <= end1

To avoid duplicate symmetric pairs, the query keeps only pairs such that
STR(?change1) < STR(?change2).

Important note
--------------
This agent detects a temporal conflict pattern, not a proof that the two
changes are semantically incompatible. It is intended as a level-1 clue.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Change Followed By Incident Detector,
- Silent Degradation After Change Detector,
- Event Burst Detector,
- Incident Propagation Detector,
- Operational Change Review.

Output
------
Results are written to:
results/dynamic/aposteriori/change_overlap_conflict_results.json
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
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?change1 ?change2 ?relatedElement
       ?start1 ?end1 ?start2 ?end2
WHERE {
  ?change1 a noria:ChangeRequest ;
           noria:eventRelatedElement ?relatedElement ;
           noria:changeRequestActualStartTime ?start1 ;
           noria:changeRequestActualEndTime ?end1 .

  ?change2 a noria:ChangeRequest ;
           noria:eventRelatedElement ?relatedElement ;
           noria:changeRequestActualStartTime ?start2 ;
           noria:changeRequestActualEndTime ?end2 .

  FILTER(?change1 != ?change2)
  FILTER(STR(?change1) < STR(?change2))

  FILTER(xsd:dateTime(?start1) <= xsd:dateTime(?end2))
  FILTER(xsd:dateTime(?start2) <= xsd:dateTime(?end1))
}
ORDER BY ?relatedElement ?start1 ?start2
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "change_overlap_conflict_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ChangeOverlapConflictDetector] Querying endpoint: {ENDPOINT}")

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
            f"[ChangeOverlapConflictDetector] "
            f"{len(results)} overlapping change conflict pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[ChangeOverlapConflictDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[ChangeOverlapConflictDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[ChangeOverlapConflictDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[ChangeOverlapConflictDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()