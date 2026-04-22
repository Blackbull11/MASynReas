"""
Critical Event Ticket Escalation Detector - Dynamic / A Posteriori

Purpose
-------
This level-1 executor agent detects patterns in the NORIA-O knowledge graph
where a critical-like EventRecord is followed by the opening of a highly
qualified TroubleTicket triggered by that event.

Business intuition
------------------
When a critical event triggers the creation of a ticket that is assigned a high
severity, high priority, or high urgency, this reflects an operational
escalation of the incident.

Such a pattern may correspond to:
- a serious fault rapidly recognized by operations,
- an event whose impact is judged important enough to escalate,
- a major incident in formation,
- or a diagnosis workflow where the event severity is confirmed by ticket
  qualification.

Interest of the query
---------------------
This is a dynamic a posteriori diagnostic check because it exploits the
temporal and semantic relation between an observed event and the operational
reaction it triggers.

It is particularly useful during diagnosis because it helps:
- identify events that led to strong operational escalation,
- distinguish weak signals from recognized major incidents,
- provide an explainable event-to-ticket diagnostic chain,
- and support higher-level incident qualification reasoning.

Detection logic
---------------
The query reports patterns where:
- an EventRecord contains critical-like wording in its log text,
- a TroubleTicket is explicitly triggered by that event,
- the ticket has at least one high qualification signal among:
  severity, priority, or urgency,
- and the ticket detection time occurs shortly after the event logging time.

Important note
--------------
This first version uses heuristic textual matching:
- criticality of the event is inferred from noria:logText,
- escalation of the ticket is inferred from current values of
  troubleTicketSeverity, troubleTicketPriority, and troubleTicketUrgency.

If your dataset contains cleaner categorical values or a real history of ticket
updates, those should later be preferred.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Stale Incident Detector,
- Reopened Incident Detector,
- Event Burst Detector,
- Incident Propagation Detector,
- Major Incident Review.

Output
------
Results are written to:
results/dynamic/aposteriori/critical_event_ticket_escalation_results.json
"""

import json
import sys
from pathlib import Path

import requests

# ============================================================
# USER-EDITABLE SECTION
# ============================================================

ENDPOINT = "http://localhost:8890/sparql"

WINDOW_MINUTES = 30

QUERY = f"""
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT ?event ?ticket ?relatedElement
       ?eventTime ?ticketTime ?logText
       ?ticketSeverity ?ticketPriority ?ticketUrgency
       (bif:datediff(
          'minute',
          xsd:dateTime(?eventTime),
          xsd:dateTime(?ticketTime)
        ) AS ?delayMinutes)
WHERE {{
  ?event a noria:EventRecord ;
         noria:eventRelatedElement ?relatedElement ;
         noria:loggingTime ?eventTime ;
         noria:logText ?logText .

  ?ticket a noria:TroubleTicket ;
          noria:troubleTicketTrigger ?event ;
          noria:troubleTicketDetectionDateTime ?ticketTime .

  OPTIONAL {{ ?ticket noria:troubleTicketSeverity ?ticketSeverity . }}
  OPTIONAL {{ ?ticket noria:troubleTicketPriority ?ticketPriority . }}
  OPTIONAL {{ ?ticket noria:troubleTicketUrgency ?ticketUrgency . }}

  BIND(LCASE(STR(?logText)) AS ?logTextLower)

  FILTER(
    REGEX(?logTextLower, "critical|major|severe|urgent|outage|failure|failed|down|unavailable")
  )

  FILTER(?ticketTime >= ?eventTime)

  FILTER(
    bif:datediff(
      'minute',
      xsd:dateTime(?eventTime),
      xsd:dateTime(?ticketTime)
    ) <= {WINDOW_MINUTES}
  )

  BIND(LCASE(COALESCE(STR(?ticketSeverity), "")) AS ?ticketSeverityLower)
  BIND(LCASE(COALESCE(STR(?ticketPriority), "")) AS ?ticketPriorityLower)
  BIND(LCASE(COALESCE(STR(?ticketUrgency), "")) AS ?ticketUrgencyLower)

  FILTER(
       REGEX(?ticketSeverityLower, "critical|major|high|severe|blocker|1")
    || REGEX(?ticketPriorityLower, "p1|p2|high|critical|major|urgent|1|2")
    || REGEX(?ticketUrgencyLower, "high|critical|urgent|immediate|1")
  )
}}
ORDER BY ?relatedElement ?eventTime ?ticketTime
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "aposteriori"
    / "critical_event_ticket_escalation_results.json"
)

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[CriticalEventTicketEscalationDetector] Querying endpoint: {ENDPOINT}")
    print(
        f"[CriticalEventTicketEscalationDetector] "
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
            f"[CriticalEventTicketEscalationDetector] "
            f"{len(results)} critical-event-to-ticket-escalation pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[CriticalEventTicketEscalationDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[CriticalEventTicketEscalationDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[CriticalEventTicketEscalationDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[CriticalEventTicketEscalationDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()