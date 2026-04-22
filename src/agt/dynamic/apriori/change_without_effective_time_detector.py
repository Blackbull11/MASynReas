"""
Change Without Effective Time Detector - Dynamic / A Priori

Purpose
-------
This level-1 executor agent detects ChangeRequest instances in the NORIA-O
knowledge graph that do not provide complete effective execution times.

Business intuition
------------------
To reason dynamically about the impact of a change, one must know when the
change actually started and/or ended.

Without effective execution times, a change cannot be:
- reliably correlated with subsequent incidents,
- used in post-change diagnosis,
- compared with overlapping changes,
- or integrated into any temporal reasoning about change impact.

Interest of the query
---------------------
This is a dynamic a priori diagnostic check because it identifies a critical
observability weakness before any temporal analysis involving changes is
attempted.

It is particularly useful because agents such as:
- Change Followed By Incident Detector,
- Change Overlap Conflict Detector,
- Silent Degradation After Change Detector,
depend directly on the availability of actual change times.

Detection logic
---------------
The query selects every ChangeRequest for which:
- no noria:changeRequestActualStartTime is present,
- or no noria:changeRequestActualEndTime is present.

The result also indicates which effective time information is missing.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Change Observability Quality Review,
- Dynamic Diagnosis Reliability Warning,
- Change Documentation Completeness Check.

Output
------
Results are written to:
results/dynamic/apriori/change_without_effective_time_results.json
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

SELECT ?change
       (BOUND(?actualStartTime) AS ?hasActualStartTime)
       (BOUND(?actualEndTime) AS ?hasActualEndTime)
WHERE {
  ?change a noria:ChangeRequest .

  OPTIONAL { ?change noria:changeRequestActualStartTime ?actualStartTime . }
  OPTIONAL { ?change noria:changeRequestActualEndTime ?actualEndTime . }

  FILTER(!BOUND(?actualStartTime) || !BOUND(?actualEndTime))
}
ORDER BY ?change
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "apriori"
    / "change_without_effective_time_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ChangeWithoutEffectiveTimeDetector] Querying endpoint: {ENDPOINT}")

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
            f"[ChangeWithoutEffectiveTimeDetector] "
            f"{len(results)} change(s) without complete effective time found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[ChangeWithoutEffectiveTimeDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[ChangeWithoutEffectiveTimeDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[ChangeWithoutEffectiveTimeDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[ChangeWithoutEffectiveTimeDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()