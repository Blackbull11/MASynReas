"""
Change Followed By Incident Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects patterns in the NORIA-O knowledge graph
where a ChangeRequest is shortly followed by an EventRecord affecting the same
related element.

Business intuition
------------------
When an incident-like event appears soon after a change has been performed on
the same network element, the change becomes a natural candidate for explaining
the observed anomaly.

Such a pattern may correspond to:
- a faulty configuration change,
- an operational intervention with unintended side effects,
- a change that destabilized the targeted element,
- or a local degradation introduced during maintenance.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it correlates the
temporal occurrence of a completed change with the subsequent observation of
an event on the same element.

It is particularly useful during diagnosis because it helps:
- orient the search toward a recent operational cause,
- distinguish spontaneous incidents from post-change incidents,
- provide an explainable temporal link between action and symptom,
- and support higher-level causal reasoning.

Detection logic
---------------
For each ChangeRequest:
- the change is linked to a related element,
- the change has an actual end time,
- an EventRecord affects the same related element,
- the event occurs after the change end time,
- and within a configurable time window.

A pattern is reported for every change/event pair satisfying these conditions.

Important note
--------------
This agent detects a temporal suspicion pattern, not a formal proof of
causality. It is intended as a level-1 diagnostic clue.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Silent Degradation After Change Detector,
- Event Burst Detector,
- Repeated Similar Event Detector,
- Incident Propagation Detector,
- Change Conflict Review.

Output
------
Results are written to:
results/dynamic/aposteriori/change_followed_by_incident_results.json
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
WINDOW_MINUTES = 30

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?change ?event ?relatedElement
       ?changeEndTime ?eventTime
       (bif:datediff(
          'minute',
          xsd:dateTime(?changeEndTime),
          xsd:dateTime(?eventTime)
        ) AS ?delayMinutes)
WHERE {{
  ?change a noria:ChangeRequest ;
          noria:eventRelatedElement ?relatedElement ;
          noria:changeRequestActualEndTime ?changeEndTime .

  ?event a noria:EventRecord ;
         noria:eventRelatedElement ?relatedElement ;
         noria:loggingTime ?eventTime .

  FILTER(?eventTime >= ?changeEndTime)

  FILTER(
    bif:datediff(
      'minute',
      xsd:dateTime(?changeEndTime),
      xsd:dateTime(?eventTime)
    ) <= {WINDOW_MINUTES}
  )
}}
ORDER BY ?relatedElement ?changeEndTime ?eventTime
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "change_followed_by_incident_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ChangeFollowedByIncidentDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[ChangeFollowedByIncidentDetector] "
        f"Window = {WINDOW_MINUTES} minute(s)."
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
            f"[ChangeFollowedByIncidentDetector] "
            f"{len(results)} change-followed-by-incident pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[ChangeFollowedByIncidentDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[ChangeFollowedByIncidentDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[ChangeFollowedByIncidentDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[ChangeFollowedByIncidentDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()