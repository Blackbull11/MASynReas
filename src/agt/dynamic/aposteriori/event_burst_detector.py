"""
Event Burst Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects local burst patterns in the NORIA-O
knowledge graph, i.e. a high number of EventRecord instances affecting the
same related element within a short time window.

Business intuition
------------------
When many events are logged in a short period on the same network element,
this often indicates an active degradation episode rather than an isolated
incident.

Such a burst may correspond to:
- a sudden instability of a resource,
- repeated alarms emitted during the same failure episode,
- a local fault producing many correlated notifications,
- or the beginning of a wider incident propagation.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it uses the temporal
distribution of observed EventRecord instances to characterize the behavior
of an already active anomaly.

It is particularly useful in diagnosis because it helps:
- identify the local focus of an incident,
- distinguish isolated events from sustained instability,
- prioritize highly active faulty elements,
- and provide an explainable temporal signal to higher-level agents.

Detection logic
---------------
For each EventRecord used as a potential window anchor, the query counts how
many EventRecord instances affect the same related element within a configurable
time window.

A pattern is reported when the number of events in that window reaches or
exceeds a configurable threshold.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Repeated Similar Event Detector,
- Flapping State Detector,
- Incident Propagation Detector,
- Change Followed By Incident Detector,
- Local Root Cause Prioritization.

Output
------
Results are written to:
results/dynamic/aposteriori/event_burst_results.json
"""

import json
import sys
from pathlib import Path

import requests

# ============================================================
# USER-EDITABLE SECTION
# ============================================================

ENDPOINT = "http://localhost:8890/sparql"

# Burst detection parameters
WINDOW_MINUTES = 5
BURST_THRESHOLD = 5

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?relatedElement ?windowStart
       (COUNT(DISTINCT ?event2) AS ?eventCount)
       (MIN(?time2) AS ?firstEventTime)
       (MAX(?time2) AS ?lastEventTime)
WHERE {{
  ?event1 a noria:EventRecord ;
          noria:eventRelatedElement ?relatedElement ;
          noria:loggingTime ?time1 .

  ?event2 a noria:EventRecord ;
          noria:eventRelatedElement ?relatedElement ;
          noria:loggingTime ?time2 .

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
GROUP BY ?relatedElement ?windowStart
HAVING (COUNT(DISTINCT ?event2) >= {BURST_THRESHOLD})
ORDER BY ?relatedElement ?windowStart
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "event_burst_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[EventBurstDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[EventBurstDetector] "
        f"Window = {WINDOW_MINUTES} minute(s), threshold = {BURST_THRESHOLD} event(s)."
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
            f"[EventBurstDetector] "
            f"{len(results)} event burst pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[EventBurstDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[EventBurstDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[EventBurstDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[EventBurstDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()