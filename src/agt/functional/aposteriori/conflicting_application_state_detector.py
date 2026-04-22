"""
Conflicting Application State Detector - Functional / A Posteriori

Purpose
-------
This level-1 executor agent detects applications that appear in conflicting
operational states at the same time in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT system, an application should have a consistent operational state
at any given time.

However, monitoring systems may sometimes produce inconsistent signals, such as:
- simultaneous FAILURE and RECOVERY events,
- conflicting severity levels,
- duplicated or unsynchronized monitoring inputs.

Such situations may indicate:
- data ingestion inconsistencies,
- monitoring system desynchronization,
- duplicated probes,
- or incorrect correlation between events and applications.

Interest of the query
---------------------
This detector identifies contradictions in application-level observations.

It is especially useful for:
- validating monitoring consistency,
- detecting noisy or unreliable signals,
- improving the quality of higher-level diagnostics,
- avoiding misleading root cause analysis.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Event Correlation Consistency Check,
- Monitoring Synchronization Verification,
- Duplicate Event Detection,
- Data Quality Assessment,
- Temporal Alignment Verification.

Output
------
Results are written to:
results/functional/aposteriori/conflicting_application_state_results.json
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

SELECT ?application ?time (COUNT(DISTINCT ?type) AS ?typeCount)
WHERE {
  ?event a noria:EventRecord ;
         noria:loggingTime ?time ;
         noria:logOriginatingManagementSystem ?application ;
         dcterms:type ?type .

  ?application a noria:Application .
}
GROUP BY ?application ?time
HAVING (COUNT(DISTINCT ?type) > 1)
ORDER BY ?application ?time
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "functional" / "aposteriori" / "conflicting_application_state_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ConflictingApplicationStateDetector] Querying endpoint: {ENDPOINT}")

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
            "[ConflictingApplicationStateDetector] "
            f"{len(results)} conflicting application state pattern(s) found."
        )

        PROJECT_ROOT.joinpath("results", "functional", "aposteriori").mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[ConflictingApplicationStateDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[ConflictingApplicationStateDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[ConflictingApplicationStateDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[ConflictingApplicationStateDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()