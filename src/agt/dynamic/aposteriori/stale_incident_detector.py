"""
Stale Incident Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects persistent unresolved incidents in the
NORIA-O knowledge graph, i.e. trouble tickets that remain active for a long
time while new EventRecord instances continue to appear on the same related
element.

Business intuition
------------------
When a ticket remains open or otherwise unresolved for a significant duration,
and the affected element continues to generate new events, this suggests that
the underlying problem has not truly been solved.

Such a pattern may correspond to:
- a persistent incident still active in production,
- an ineffective corrective action,
- an unresolved root cause,
- or a long-running degradation repeatedly producing symptoms.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it combines:
- the age of an already existing trouble ticket,
- its current unresolved status,
- and the continued appearance of new event evidence on the same element.

It is particularly useful during diagnosis because it helps:
- avoid treating the situation as a brand-new incident,
- identify persistent operational issues,
- prioritize long-lasting unresolved failures,
- and provide an explainable link between ticket lifecycle and observed events.

Detection logic
---------------
The query reports patterns where:
- a TroubleTicket has a related element,
- the ticket has a detection datetime,
- the ticket has a current status suggesting it is still unresolved,
- the ticket is older than a configurable age threshold,
- and at least one EventRecord on the same related element is logged after
  the ticket detection time.

The results aggregate the number of subsequent events and the time span of
those continued symptoms.

Important note
--------------
This first version assumes:
- the ticket is connected to the impacted object through
  noria:troubleTicketImpacts,
- the current status is stored in noria:troubleTicketStatusCurrent,
- unresolved statuses can be approximated through textual matching.

If your dataset uses a different relation between tickets and impacted
resources/services, or a controlled vocabulary for statuses, the query should
be adapted accordingly.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Reopened Incident Detector,
- Repeated Similar Event Detector,
- Event Burst Detector,
- Incident Propagation Detector,
- Ticket Handling Review.

Output
------
Results are written to:
results/dynamic/aposteriori/stale_incident_results.json
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
MIN_TICKET_AGE_DAYS = 2
MIN_FOLLOWUP_EVENTS = 1

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?ticket ?relatedElement ?ticketTime ?ticketStatus
       (COUNT(DISTINCT ?event) AS ?followupEventCount)
       (MIN(?eventTime) AS ?firstFollowupEventTime)
       (MAX(?eventTime) AS ?lastFollowupEventTime)
WHERE {{
  ?ticket a noria:TroubleTicket ;
          noria:troubleTicketImpacts ?relatedElement ;
          noria:troubleTicketDetectionDateTime ?ticketTime ;
          noria:troubleTicketStatusCurrent ?ticketStatus .

  ?event a noria:EventRecord ;
         noria:eventRelatedElement ?relatedElement ;
         noria:loggingTime ?eventTime .

  FILTER(?eventTime >= ?ticketTime)

  BIND(LCASE(STR(?ticketStatus)) AS ?ticketStatusLower)

  FILTER(
       REGEX(?ticketStatusLower, "open")
    || REGEX(?ticketStatusLower, "ongoing")
    || REGEX(?ticketStatusLower, "in progress")
    || REGEX(?ticketStatusLower, "assigned")
    || REGEX(?ticketStatusLower, "pending")
    || REGEX(?ticketStatusLower, "investigating")
  )

  FILTER(
    bif:datediff(
      'day',
      xsd:dateTime(?ticketTime),
      now()
    ) >= {MIN_TICKET_AGE_DAYS}
  )
}}
GROUP BY ?ticket ?relatedElement ?ticketTime ?ticketStatus
HAVING (COUNT(DISTINCT ?event) >= {MIN_FOLLOWUP_EVENTS})
ORDER BY ?ticketTime ?ticket
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "stale_incident_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[StaleIncidentDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[StaleIncidentDetector] "
        f"Minimum age = {MIN_TICKET_AGE_DAYS} day(s), "
        f"minimum follow-up events = {MIN_FOLLOWUP_EVENTS}."
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
            f"[StaleIncidentDetector] "
            f"{len(results)} stale incident pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[StaleIncidentDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[StaleIncidentDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[StaleIncidentDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[StaleIncidentDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()