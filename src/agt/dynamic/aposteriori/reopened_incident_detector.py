"""
Reopened Incident Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects reopened or effectively reopened incident
patterns in the NORIA-O knowledge graph, i.e. situations where a recently
closed trouble ticket is followed by a new active trouble ticket affecting
the same related element.

Business intuition
------------------
When a ticket is marked as closed or resolved, but a new ticket is opened
soon afterwards on the same element, this often indicates that the original
problem was not fully solved, that the root cause was not removed, or that
the incident has recurred.

Such a pattern may correspond to:
- an incomplete resolution,
- a recurring fault,
- a premature closure of the previous ticket,
- or an unstable situation that was believed to be fixed.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it uses the temporal
succession of trouble tickets on the same related element to identify incident
recurrence.

It is particularly useful during diagnosis because it helps:
- distinguish genuinely new incidents from recurring ones,
- identify cases where the previous resolution may have been insufficient,
- provide an explainable incident lifecycle signal,
- and orient the diagnosis toward persistent underlying causes.

Detection logic
---------------
The query reports patterns where:
- a first TroubleTicket affects a related element,
- this first ticket has a current status suggesting closure or resolution,
- a second distinct TroubleTicket affects the same related element,
- the second ticket has a current status suggesting it is active,
- and the second ticket is detected within a configurable time window after
  the first ticket.

This first version approximates "reopened incident" through ticket recurrence
on the same element, rather than through explicit history on a single ticket.

Important note
--------------
This implementation assumes:
- tickets are linked to impacted elements through (noria:troubleTicketRelatedResource | (dct:relation/noria:logOriginatingManagedObject)),
- ticket times are stored in noria:troubleTicketDetectionDateTime,
- current ticket statuses are stored in noria:troubleTicketStatusCurrent.

If your dataset contains a true status history for the same ticket, a more
precise reopened-incident detector could later be built on top of that.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Stale Incident Detector,
- Repeated Similar Event Detector,
- Event Burst Detector,
- Root Cause Persistence Review,
- Ticket Resolution Quality Review.

Output
------
Results are written to:
results/dynamic/aposteriori/reopened_incident_results.json
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
REOPEN_WINDOW_DAYS = 7

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX dct:   <http://purl.org/dc/terms/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?closedTicket ?newTicket ?relatedElement
       ?closedTicketTime ?newTicketTime
       ?closedStatus ?newStatus
       (bif:datediff(
          'day',
          xsd:dateTime(?closedTicketTime),
          xsd:dateTime(?newTicketTime)
        ) AS ?delayDays)
WHERE {{
  ?closedTicket a noria:TroubleTicket ;
                (noria:troubleTicketRelatedResource | (dct:relation/noria:logOriginatingManagedObject)) ?relatedElement ;
                noria:troubleTicketDetectionDateTime ?closedTicketTime ;
                noria:troubleTicketStatusCurrent ?closedStatus .

  ?newTicket a noria:TroubleTicket ;
             (noria:troubleTicketRelatedResource | (dct:relation/noria:logOriginatingManagedObject)) ?relatedElement ;
             noria:troubleTicketDetectionDateTime ?newTicketTime ;
             noria:troubleTicketStatusCurrent ?newStatus .

  FILTER(?closedTicket != ?newTicket)
  FILTER(?newTicketTime > ?closedTicketTime)

  BIND(LCASE(STR(?closedStatus)) AS ?closedStatusLower)
  BIND(LCASE(STR(?newStatus)) AS ?newStatusLower)

  FILTER(
       REGEX(?closedStatusLower, "closed")
    || REGEX(?closedStatusLower, "resolved")
    || REGEX(?closedStatusLower, "restored")
    || REGEX(?closedStatusLower, "completed")
    || REGEX(?closedStatusLower, "done")
  )

  FILTER(
       REGEX(?newStatusLower, "open")
    || REGEX(?newStatusLower, "ongoing")
    || REGEX(?newStatusLower, "in progress")
    || REGEX(?newStatusLower, "assigned")
    || REGEX(?newStatusLower, "pending")
    || REGEX(?newStatusLower, "investigating")
  )

  FILTER(
    bif:datediff(
      'day',
      xsd:dateTime(?closedTicketTime),
      xsd:dateTime(?newTicketTime)
    ) <= {REOPEN_WINDOW_DAYS}
  )

  FILTER(STR(?closedTicket) < STR(?newTicket))
}}
ORDER BY ?relatedElement ?closedTicketTime ?newTicketTime
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "reopened_incident_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ReopenedIncidentDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[ReopenedIncidentDetector] "
        f"Reopen window = {REOPEN_WINDOW_DAYS} day(s)."
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
            f"[ReopenedIncidentDetector] "
            f"{len(results)} reopened incident pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[ReopenedIncidentDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[ReopenedIncidentDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[ReopenedIncidentDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[ReopenedIncidentDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()