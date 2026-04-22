"""
Repeated Similar Event Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects repeated similar EventRecord instances
affecting the same related element within a short time window in the NORIA-O
knowledge graph.

Business intuition
------------------
When the same or very similar event is logged several times on the same
network element in a limited time interval, this often indicates that the
underlying problem is persistent, intermittent, or insufficiently resolved.

Such a pattern may correspond to:
- a chronic local fault,
- an unstable component generating recurring alarms,
- an incident that temporarily disappears and reappears,
- or an ineffective corrective action.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it relies on the
temporal repetition of already observed EventRecord instances.

It is particularly useful during diagnosis because it helps:
- distinguish persistent faults from isolated events,
- identify noisy but meaningful recurring symptoms,
- orient the diagnosis toward a local recurring cause,
- and provide an explainable signal for higher-level correlation agents.

Detection logic
---------------
For each candidate event used as a temporal anchor, the query counts how many
EventRecord instances:
- affect the same related element,
- share the same log text,
- and occur within a configurable time window.

A pattern is reported when this count reaches or exceeds a configurable
threshold.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Event Burst Detector,
- Flapping State Detector,
- Stale Incident Detector,
- Incident Propagation Detector,
- Local Root Cause Prioritization.

Output
------
Results are written to:
results/dynamic/aposteriori/repeated_similar_event_results.json
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
REPETITION_THRESHOLD = 3

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?relatedElement ?logText ?windowStart
       (COUNT(DISTINCT ?event2) AS ?eventCount)
       (MIN(?time2) AS ?firstEventTime)
       (MAX(?time2) AS ?lastEventTime)
WHERE {{
  ?event1 a noria:EventRecord ;
          noria:eventRelatedElement ?relatedElement ;
          noria:loggingTime ?time1 ;
          noria:logText ?logText .

  ?event2 a noria:EventRecord ;
          noria:eventRelatedElement ?relatedElement ;
          noria:loggingTime ?time2 ;
          noria:logText ?logText .

  FILTER(?time2 >= ?time1)
  FILTER(
    bif:datediff(
      'minute',
      xsd:dateTime(?time1),
      xsd:dateTime(?time2)
    ) <= {WINDOW_MINUTES}
  )

  BIND(?time1 AS ?windowStart)
}}
GROUP BY ?relatedElement ?logText ?windowStart
HAVING (COUNT(DISTINCT ?event2) >= {REPETITION_THRESHOLD})
ORDER BY ?relatedElement ?logText ?windowStart
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "repeated_similar_event_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[RepeatedSimilarEventDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[RepeatedSimilarEventDetector] "
        f"Window = {WINDOW_MINUTES} minute(s), threshold = {REPETITION_THRESHOLD} event(s)."
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
            f"[RepeatedSimilarEventDetector] "
            f"{len(results)} repeated similar event pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[RepeatedSimilarEventDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[RepeatedSimilarEventDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[RepeatedSimilarEventDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[RepeatedSimilarEventDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()