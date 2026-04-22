"""
Silent Degradation After Change Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects patterns in the NORIA-O knowledge graph
where a completed ChangeRequest is followed by a progressive accumulation of
weak or non-critical EventRecord instances on the same related element.

Business intuition
------------------
Not every problematic change causes an immediate major incident. Sometimes,
a change is followed by a silent degradation: the system keeps running, but
small warning-like, degraded, unstable, or repeated low-intensity events begin
to appear.

Such a pattern may correspond to:
- a change that subtly destabilized the element,
- a gradual post-change degradation,
- a latent configuration issue,
- or an operational side effect that did not immediately trigger a major alarm.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it correlates a past
change with the subsequent temporal accumulation of mild event symptoms on the
same element.

It is particularly useful during diagnosis because it helps:
- detect post-change degradations that are not immediately catastrophic,
- distinguish silent deterioration from abrupt failure,
- provide an explainable temporal clue linking weak symptoms to a recent change,
- and support higher-level post-change analysis.

Detection logic
---------------
For each ChangeRequest:
- the change affects a related element,
- the change has an actual end time,
- EventRecord instances affect the same related element after that end time,
- the events occur within a configurable monitoring window,
- the events are weak-like according to heuristic textual matching,
- and the number of such events reaches a configurable threshold.

Important note
--------------
This first version uses heuristic textual matching on noria:logText to
approximate weak/non-critical symptoms. It excludes strongly critical wording.

If your dataset contains a structured event type, severity, alarm class,
or probable cause field, it would be preferable to use that instead.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Change Followed By Incident Detector,
- Repeated Similar Event Detector,
- Event Burst Detector,
- Stale Incident Detector,
- Post-Change Review.

Output
------
Results are written to:
results/dynamic/aposteriori/silent_degradation_after_change_results.json
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
MONITORING_WINDOW_MINUTES = 180
MIN_WEAK_EVENTS = 3

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?change ?relatedElement ?changeEndTime
       (COUNT(DISTINCT ?event) AS ?weakEventCount)
       (MIN(?eventTime) AS ?firstWeakEventTime)
       (MAX(?eventTime) AS ?lastWeakEventTime)
WHERE {{
  ?change a noria:ChangeRequest ;
          noria:eventRelatedElement ?relatedElement ;
          noria:changeRequestActualEndTime ?changeEndTime .

  ?event a noria:EventRecord ;
         noria:eventRelatedElement ?relatedElement ;
         noria:loggingTime ?eventTime ;
         noria:logText ?logText .

  FILTER(?eventTime >= ?changeEndTime)

  FILTER(
    bif:datediff(
      'minute',
      xsd:dateTime(?changeEndTime),
      xsd:dateTime(?eventTime)
    ) <= {MONITORING_WINDOW_MINUTES}
  )

  BIND(LCASE(STR(?logText)) AS ?logTextLower)

  # Weak / silent degradation indicators
  BIND(
    IF(
      REGEX(
        ?logTextLower,
        "warning|degraded|degradation|slow|latency|unstable|instability|retry|retransmission|minor|intermittent|flap|packet loss|timeout"
      ),
      1,
      0
    ) AS ?isWeakLike
  )

  # Strongly critical indicators to exclude
  BIND(
    IF(
      REGEX(
        ?logTextLower,
        "critical|major|severe|outage|failure|failed|down|unavailable|unreachable"
      ),
      1,
      0
    ) AS ?isCriticalLike
  )

  FILTER(?isWeakLike = 1)
  FILTER(?isCriticalLike = 0)
}}
GROUP BY ?change ?relatedElement ?changeEndTime
HAVING (COUNT(DISTINCT ?event) >= {MIN_WEAK_EVENTS})
ORDER BY ?relatedElement ?changeEndTime
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "silent_degradation_after_change_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[SilentDegradationAfterChangeDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[SilentDegradationAfterChangeDetector] "
        f"Monitoring window = {MONITORING_WINDOW_MINUTES} minute(s), "
        f"minimum weak events = {MIN_WEAK_EVENTS}."
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
            f"[SilentDegradationAfterChangeDetector] "
            f"{len(results)} silent degradation after change pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[SilentDegradationAfterChangeDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[SilentDegradationAfterChangeDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[SilentDegradationAfterChangeDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[SilentDegradationAfterChangeDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()