"""
Ticket Without Assigned Procedure Detector - Procedural / A Priori

Purpose
-------
This level-1 executor agent detects TroubleTicket instances that are not
associated with any operational procedure in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, when an incident ticket is created, operations teams
should ideally have at least one identified remediation procedure, playbook,
or recommended repair action to guide diagnosis and resolution.

If a TroubleTicket exists but no procedure can be associated with it through
its linked event records, this may indicate:
- missing operational playbooks,
- incomplete capitalization of incident-response knowledge,
- weak standardization of corrective actions,
- or incomplete linkage between supervision and remediation knowledge.

Interest of the query
---------------------
This is a core procedural preparedness check at the interface between
incident management and remediation guidance.

It is especially useful in a priori analysis because it highlights tickets
or ticket categories that are not backed by actionable procedural knowledge.
In real operations, such situations tend to increase response time, operator
uncertainty, and variability in incident handling.

Operational modeling choice
---------------------------
In this detector, an "assigned procedure" is operationalized through the
presence of a procedure proposed by one of the event records linked to the
ticket, typically via:
- noria:troubleTicketTrigger
- or dcterms:relation
combined with:
- noria:alarmProposedRepairAction -> pep:Procedure

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Missing Standard Operating Procedure Check,
- Ticket Resolution Readiness Analysis,
- Incident Playbook Coverage Detector,
- Event-to-Procedure Mapping Verification,
- Operational Knowledge Capitalization Review.

Output
------
Results are written to:
results/procedural/apriori/ticket_without_assigned_procedure_results.json
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

SELECT DISTINCT ?ticket ?status ?priority ?severity
WHERE {
  ?ticket a noria:TroubleTicket .

  OPTIONAL { ?ticket noria:troubleTicketStatus ?status . }
  OPTIONAL { ?ticket noria:troubleTicketPriority ?priority . }
  OPTIONAL { ?ticket noria:troubleTicketSeverity ?severity . }

  FILTER NOT EXISTS {
    {
      ?ticket noria:troubleTicketTrigger ?event .
    }
    UNION
    {
      ?ticket dcterms:relation ?event .
      ?event a noria:EventRecord .
    }

    ?event noria:alarmProposedRepairAction ?procedure .
    ?procedure a <https://w3id.org/pep/Procedure> .
  }
}
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "procedural" / "apriori" / "ticket_without_assigned_procedure_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[TicketWithoutAssignedProcedureDetector] Querying endpoint: {ENDPOINT}")

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

        print(f"[TicketWithoutAssignedProcedureDetector] {len(results)} ticket(s) without assigned procedure found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[TicketWithoutAssignedProcedureDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[TicketWithoutAssignedProcedureDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[TicketWithoutAssignedProcedureDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[TicketWithoutAssignedProcedureDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()