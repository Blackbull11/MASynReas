"""
Parent Child Event Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects correlated EventRecord pairs affecting
structurally related parent/child elements in the NORIA-O knowledge graph.

Business intuition
------------------
When events are observed on both a child element and its parent resource within
a short time interval, this often indicates a meaningful local/global link in
the incident dynamics.

Such a pattern may correspond to:
- a local fault on a child component that is reflected at parent level,
- a parent-level degradation that affects one of its subcomponents,
- a coherent multi-level symptom of the same incident,
- or a useful diagnostic clue for root-cause orientation.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it uses the temporal
co-occurrence of already observed EventRecord instances on structurally related
elements.

It is particularly useful during diagnosis because it helps:
- connect local and aggregated symptoms,
- identify whether an observed anomaly has a more local or more global
  structural context,
- provide an explainable parent/child correlation signal,
- and support higher-level reasoning on incident localization.

Detection logic
---------------
For each pair of events:
- one event affects a child element,
- another event affects its parent element,
- both occur within a configurable time window.

The query reports the event pair, the corresponding elements, their times, and
the temporal order between the two events.

Important note
--------------
This first version relies on the structural relation noria:partOf to define the
parent/child link. It detects temporal correlation, not strict causality.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Incident Propagation Detector,
- Repeated Similar Event Detector,
- Event Burst Detector,
- Local Root Cause Prioritization,
- Parent/Child Structural Consistency Review.

Output
------
Results are written to:
results/dynamic/aposteriori/parent_child_event_results.json
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

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?childEvent ?parentEvent
       ?childElement ?parentElement
       ?childTime ?parentTime
       ?temporalOrder
WHERE {{
  ?childElement noria:partOf ?parentElement .

  ?childEvent a noria:EventRecord ;
              noria:eventRelatedElement ?childElement ;
              noria:loggingTime ?childTime .

  ?parentEvent a noria:EventRecord ;
               noria:eventRelatedElement ?parentElement ;
               noria:loggingTime ?parentTime .

  FILTER(?childEvent != ?parentEvent)

  FILTER(
    ABS(
      bif:datediff(
        'minute',
        xsd:dateTime(?childTime),
        xsd:dateTime(?parentTime)
      )
    ) <= {WINDOW_MINUTES}
  )

  BIND(
    IF(
      ?childTime < ?parentTime,
      "child_before_parent",
      IF(
        ?parentTime < ?childTime,
        "parent_before_child",
        "simultaneous"
      )
    ) AS ?temporalOrder
  )
}}
ORDER BY ?parentElement ?childElement ?childTime ?parentTime
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "parent_child_event_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ParentChildEventDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[ParentChildEventDetector] "
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
            f"[ParentChildEventDetector] "
            f"{len(results)} parent/child event pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[ParentChildEventDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[ParentChildEventDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[ParentChildEventDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[ParentChildEventDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()