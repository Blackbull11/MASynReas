"""
Incident Propagation Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects local incident propagation patterns in the
NORIA-O knowledge graph, i.e. cases where an event affecting one element is
shortly followed by an event affecting a structurally adjacent element.

Business intuition
------------------
When a fault appears on one network element and very shortly afterwards a new
event appears on a neighboring or hierarchically related element, this may
indicate that the incident is propagating through the network rather than
remaining purely local.

Such a pattern may correspond to:
- a local failure producing downstream effects,
- a degraded child component affecting its parent resource,
- a parent resource degradation impacting one of its subcomponents,
- or a chain of closely related symptoms spreading through the system.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it exploits the
temporal succession of already observed EventRecord instances to suggest a
local propagation mechanism.

It is particularly useful during diagnosis because it helps:
- distinguish isolated incidents from spreading disturbances,
- identify a plausible local source and an affected neighbor,
- produce an explainable causal orientation,
- and support higher-level multi-agent reasoning.

Detection logic
---------------
For each pair of events:
- event1 affects a source element at time t1,
- event2 affects a distinct target element at time t2,
- t2 occurs shortly after t1,
- source and target are structurally adjacent through a simple partOf relation
  in either direction.

A propagation pattern is reported when the second event occurs within a
configurable time window after the first one.

Important note
--------------
This first version approximates "propagation" using:
- temporal proximity,
- and structural adjacency through noria:partOf.

If your graph contains richer dependency relations, those should later be
preferred for a more precise propagation model.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Event Burst Detector,
- Repeated Similar Event Detector,
- Parent Child Event Escalation Detector,
- Change Followed By Incident Detector,
- Local Root Cause Prioritization.

Output
------
Results are written to:
results/dynamic/aposteriori/incident_propagation_results.json
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

SELECT ?sourceEvent ?targetEvent
       ?sourceElement ?targetElement
       ?sourceTime ?targetTime
       ?relationType
WHERE {{
  ?sourceEvent a noria:EventRecord ;
               noria:eventRelatedElement ?sourceElement ;
               noria:loggingTime ?sourceTime .

  ?targetEvent a noria:EventRecord ;
               noria:eventRelatedElement ?targetElement ;
               noria:loggingTime ?targetTime .

  FILTER(?sourceEvent != ?targetEvent)
  FILTER(?sourceElement != ?targetElement)
  FILTER(?targetTime >= ?sourceTime)

  FILTER(
    bif:datediff(
      'minute',
      xsd:dateTime(?sourceTime),
      xsd:dateTime(?targetTime)
    ) <= {WINDOW_MINUTES}
  )

  {{
    ?targetElement noria:partOf ?sourceElement .
    BIND("child_to_parent" AS ?relationType)
  }}
  UNION
  {{
    ?sourceElement noria:partOf ?targetElement .
    BIND("parent_to_child" AS ?relationType)
  }}
}}
ORDER BY ?sourceElement ?sourceTime ?targetTime ?targetElement
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "incident_propagation_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[IncidentPropagationDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[IncidentPropagationDetector] "
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
            f"[IncidentPropagationDetector] "
            f"{len(results)} incident propagation pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[IncidentPropagationDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[IncidentPropagationDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[IncidentPropagationDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[IncidentPropagationDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()