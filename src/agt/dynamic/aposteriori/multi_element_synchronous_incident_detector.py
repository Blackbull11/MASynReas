"""
Multi Element Synchronous Incident Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects patterns in the NORIA-O knowledge graph
where several distinct related elements are affected by EventRecord instances
within a short common time window.

Business intuition
------------------
When multiple different network elements generate events almost at the same
time, this may indicate that the observed anomaly is not purely local.

Such a pattern may correspond to:
- a common upstream cause,
- a shared dependency failure,
- a synchronized service degradation,
- or a distributed incident episode affecting several elements at once.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it uses the temporal
co-occurrence of already observed EventRecord instances on multiple distinct
elements.

It is particularly useful during diagnosis because it helps:
- identify potentially systemic incidents,
- distinguish local faults from multi-element episodes,
- provide an explainable synchronous incident signal,
- and orient higher-level reasoning toward a shared root cause.

Detection logic
---------------
For each candidate anchor event:
- a short time window starts at the anchor event time,
- all EventRecord instances within that window are collected,
- the query counts how many distinct related elements are affected,
- and how many distinct events are observed overall.

A pattern is reported when the number of distinct affected elements reaches or
exceeds a configurable threshold.

Important note
--------------
This first version detects temporal synchrony only. It does not require the
elements to be structurally adjacent or functionally linked.

If your graph later contains dependency relations that should constrain the
interpretation, the query can be refined accordingly.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Incident Propagation Detector,
- Parent Child Event Detector,
- Event Burst Detector,
- Critical Event Ticket Escalation Detector,
- Shared Cause Investigation.

Output
------
Results are written to:
results/dynamic/aposteriori/multi_element_synchronous_incident_results.json
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
WINDOW_MINUTES = 5
MIN_DISTINCT_ELEMENTS = 3
MIN_TOTAL_EVENTS = 3

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?windowStart
       (COUNT(DISTINCT ?event2) AS ?eventCount)
       (COUNT(DISTINCT ?relatedElement2) AS ?affectedElementCount)
       (MIN(?time2) AS ?firstEventTime)
       (MAX(?time2) AS ?lastEventTime)
WHERE {{
  ?event1 a noria:EventRecord ;
          noria:loggingTime ?time1 .

  ?event2 a noria:EventRecord ;
          noria:eventRelatedElement ?relatedElement2 ;
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
GROUP BY ?windowStart
HAVING (
  COUNT(DISTINCT ?relatedElement2) >= {MIN_DISTINCT_ELEMENTS}
  &&
  COUNT(DISTINCT ?event2) >= {MIN_TOTAL_EVENTS}
)
ORDER BY ?windowStart
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "multi_element_synchronous_incident_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[MultiElementSynchronousIncidentDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[MultiElementSynchronousIncidentDetector] "
        f"Window = {WINDOW_MINUTES} minute(s), "
        f"minimum distinct elements = {MIN_DISTINCT_ELEMENTS}, "
        f"minimum total events = {MIN_TOTAL_EVENTS}."
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
            f"[MultiElementSynchronousIncidentDetector] "
            f"{len(results)} multi-element synchronous incident pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[MultiElementSynchronousIncidentDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[MultiElementSynchronousIncidentDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[MultiElementSynchronousIncidentDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[MultiElementSynchronousIncidentDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()