"""
Ticket Without Linked Event Detector - Procedural / A Posteriori

Purpose
-------
This level-1 executor agent detects TroubleTicket instances that are not linked
to any EventRecord in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, a trouble ticket should normally be supported by one or more
observed events, alarms, or logs that justify its creation and help explain
its operational context.

If a TroubleTicket exists but is not linked to any EventRecord, this may indicate:
- incomplete incident documentation,
- manual ticket creation without observable trace,
- broken correlation between supervision and ticketing systems,
- or incomplete ingestion of monitoring/event data.

Interest of the query
---------------------
This is a core procedural consistency check between the incident management
layer and the event management layer.

It is especially useful in a posteriori analysis because it reveals tickets
whose operational justification is not visible in the graph. Such tickets are
harder to audit, diagnose, correlate, or prioritize properly.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Event-to-Ticket Correlation Recovery,
- Incident Qualification Consistency Check,
- Missing Incident Trace Detector,
- Ticket Documentation Completeness Check,
- Monitoring / Ticketing Integration Analysis.

Output
------
Results are written to:
results/procedural/aposteriori/ticket_without_linked_event_results.json
"""

import json
import sys
from pathlib import Path

import requests

# ============================================================
# USER-EDITABLE SECTION
# ============================================================

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?ticket ?status ?creationDate
WHERE {
  ?ticket a noria:TroubleTicket .

  OPTIONAL { ?ticket noria:documentStatus ?status . }
  OPTIONAL { ?ticket noria:ticketEntryDate ?creationDate . }

  FILTER NOT EXISTS {
    ?ticket dcterms:relation ?event .
    ?event a noria:EventRecord .
  }

  FILTER NOT EXISTS {
    ?ticket noria:documentStatusHistory ?event2 .
    ?event2 a noria:EventRecord .
  }
}
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "procedural" / "aposteriori" / "ticket_without_linked_event_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[TicketWithoutLinkedEventDetector] Querying endpoint: {ENDPOINT}")

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

        print(f"[TicketWithoutLinkedEventDetector] {len(results)} ticket(s) without linked event found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[TicketWithoutLinkedEventDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[TicketWithoutLinkedEventDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[TicketWithoutLinkedEventDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[TicketWithoutLinkedEventDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()