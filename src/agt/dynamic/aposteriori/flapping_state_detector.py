"""
Flapping State Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects flapping patterns in the NORIA-O knowledge
graph, i.e. rapid alternation of contradictory state-related EventRecord
instances affecting the same related element.

Business intuition
------------------
When a network element repeatedly alternates between opposite states such as
UP and DOWN within a short time interval, this often indicates an unstable
component, an intermittent fault, a degraded link, or a local control issue.

Such a pattern is more informative than a single failure event because it
suggests oscillation rather than a clean transition to a failed state.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it uses the temporal
organization of observed events to identify a characteristic instability
pattern.

It is particularly useful during diagnosis because it helps:
- identify unstable resources rather than isolated failures,
- distinguish intermittent faults from persistent outages,
- provide an explainable signal of oscillation,
- and orient further diagnosis toward local dynamic instability.

Detection logic
---------------
For each related element and each anchor event, the query considers a short
time window and counts state-related events whose log text suggests either:
- a DOWN-like state, or
- an UP-like state.

A flapping pattern is reported when:
- the number of state-related events in the window reaches a minimum threshold,
- at least one DOWN-like event is present,
- and at least one UP-like event is present.

Important note
--------------
This implementation uses heuristic keyword matching on noria:logText.
If your dataset contains a cleaner property for event type or state transition,
it would be better to use that property instead of textual matching.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Repeated Similar Event Detector,
- Event Burst Detector,
- Incident Propagation Detector,
- Change Followed By Incident Detector,
- Local Resource Instability Analysis.

Output
------
Results are written to:
results/dynamic/aposteriori/flapping_state_results.json
"""

import json
import sys
from pathlib import Path

import requests

# ============================================================
# USER-EDITABLE SECTION
# ============================================================

ENDPOINT = "http://localhost:8890/sparql"

# Detection parameters
WINDOW_MINUTES = 10
MIN_STATE_CHANGE_EVENTS = 3

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?relatedElement ?windowStart
       (COUNT(DISTINCT ?event2) AS ?stateEventCount)
       (SUM(?isDownLike) AS ?downLikeCount)
       (SUM(?isUpLike) AS ?upLikeCount)
       (MIN(?time2) AS ?firstEventTime)
       (MAX(?time2) AS ?lastEventTime)
WHERE {{
  ?event1 a noria:EventRecord ;
          noria:eventRelatedElement ?relatedElement ;
          noria:loggingTime ?time1 .

  ?event2 a noria:EventRecord ;
          noria:eventRelatedElement ?relatedElement ;
          noria:loggingTime ?time2 ;
          noria:logText ?logText2 .

  FILTER(?time2 >= ?time1)
  FILTER(
    bif:datediff(
      'minute',
      xsd:dateTime(?time1),
      xsd:dateTime(?time2)
    ) <= {WINDOW_MINUTES}
  )

  BIND(LCASE(STR(?logText2)) AS ?logTextLower)

  BIND(
    IF(
      REGEX(?logTextLower, "down|unavailable|unreachable|lost|failure|failed|alarm"),
      1,
      0
    ) AS ?isDownLike
  )

  BIND(
    IF(
      REGEX(?logTextLower, "up|restored|reachable|available|recovered|clear|cleared"),
      1,
      0
    ) AS ?isUpLike
  )

  FILTER(?isDownLike = 1 || ?isUpLike = 1)

  BIND(?time1 AS ?windowStart)
}}
GROUP BY ?relatedElement ?windowStart
HAVING (
  COUNT(DISTINCT ?event2) >= {MIN_STATE_CHANGE_EVENTS}
  &&
  SUM(?isDownLike) >= 1
  &&
  SUM(?isUpLike) >= 1
)
ORDER BY ?relatedElement ?windowStart
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "flapping_state_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[FlappingStateDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[FlappingStateDetector] "
        f"Window = {WINDOW_MINUTES} minute(s), "
        f"minimum state-related events = {MIN_STATE_CHANGE_EVENTS}."
    )

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
            f"[FlappingStateDetector] "
            f"{len(results)} flapping state pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[FlappingStateDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[FlappingStateDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[FlappingStateDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[FlappingStateDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()