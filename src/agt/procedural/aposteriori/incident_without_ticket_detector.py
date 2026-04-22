"""
Incident Without Ticket Detector - Procedural / A Posteriori

Purpose
-------
This level-1 executor agent detects incident-like EventRecord instances that
are not linked to any TroubleTicket in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, a significant incident observed through the monitoring or
logging systems should normally lead to the creation of a Trouble Ticket, or
at least be explicitly correlated to one.

If an EventRecord suggests an incident situation but is not associated with
any TroubleTicket, this may indicate:
- missing incident formalization,
- incomplete operational traceability,
- a monitoring alert that never entered the support workflow,
- or incomplete ingestion of incident management data.

Interest of the query
---------------------
This is a core procedural consistency check between the event management layer
and the incident management layer.

It is especially useful in a posteriori analysis because it reveals situations
where the system observed a potentially important incident, but the operational
process did not produce the expected ticketing artifact. In such a case, later
diagnosis, escalation analysis, and auditability are weakened.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Ticket Creation Consistency Check,
- Incident Escalation Verification,
- Event-to-Ticket Correlation Recovery,
- Incident Traceability Completeness Check,
- Operational Process Gap Analysis.

Output
------
Results are written to:
results/procedural/aposteriori/incident_without_ticket_results.json
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

SELECT ?event ?severity ?time ?relatedElement
WHERE {
  ?event a noria:EventRecord ;
         noria:alarmSeverity ?severity .

  OPTIONAL { ?event noria:loggingTime ?time . }
  OPTIONAL { ?event noria:eventRelatedElement ?relatedElement . }

  FILTER NOT EXISTS {
    ?ticket a noria:TroubleTicket ;
            dcterms:relation ?event .
  }

  FILTER NOT EXISTS {
    ?ticket2 a noria:TroubleTicket ;
             noria:documentStatusHistory ?event .
  }
}
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "procedural" / "aposteriori" / "incident_without_ticket_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[IncidentWithoutTicketDetector] Querying endpoint: {ENDPOINT}")

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

        print(f"[IncidentWithoutTicketDetector] {len(results)} incident event(s) without ticket found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[IncidentWithoutTicketDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[IncidentWithoutTicketDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[IncidentWithoutTicketDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[IncidentWithoutTicketDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()