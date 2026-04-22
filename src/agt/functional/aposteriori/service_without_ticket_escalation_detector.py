"""
Service Without Ticket Escalation Detector - Functional / A Posteriori

Purpose
-------
This level-1 executor agent detects services that are impacted by technical
events through the functional support chain in the NORIA-O knowledge graph,
but for which no related trouble ticket is associated with the supporting
resources.

Business intuition
------------------
In an ICT network, when a service is impacted by incidents originating from
its supporting infrastructure, this should normally trigger some operational
follow-up, such as the creation of a trouble ticket.

If a service is impacted by one or more events but no ticket is linked to the
corresponding support resources, this may indicate:
- missing escalation,
- incomplete operational handling,
- supervision without ticketing follow-up,
- or an inconsistency between monitoring and incident management layers.

Interest of the query
---------------------
This detector is useful in a posteriori diagnosis because it highlights
service-impact situations that appear operationally unmanaged.

It helps:
- identify escalation gaps,
- detect weak coordination between monitoring and ticketing,
- improve incident handling completeness,
- and flag potentially under-managed service incidents.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Trouble Ticket Coverage Check,
- Incident Escalation Verification,
- Monitoring-to-Ticketing Consistency Check,
- Service Criticality Reassessment,
- Operational Response Completeness Check.

Output
------
Results are written to:
results/functional/aposteriori/service_without_ticket_escalation_results.json
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
PREFIX seas: <https://w3id.org/seas/>

SELECT DISTINCT ?service
WHERE {
  ?event a noria:EventRecord ;
         noria:logOriginatingManagedObject ?resource .

  ?resource noria:resourceForApplication ?application .

  ?module a noria:ApplicationModule ;
          noria:applicationModuleOf ?application ;
          seas:subSystemOf ?service .

  ?service a noria:Service .

  FILTER NOT EXISTS {
    ?ticket a noria:TroubleTicket ;
            noria:troubleTicketRelatedResource ?resource .
  }
}
ORDER BY ?service
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "functional" / "aposteriori" / "service_without_ticket_escalation_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ServiceWithoutTicketEscalationDetector] Querying endpoint: {ENDPOINT}")

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
            "[ServiceWithoutTicketEscalationDetector] "
            f"{len(results)} service(s) without ticket escalation found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[ServiceWithoutTicketEscalationDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[ServiceWithoutTicketEscalationDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[ServiceWithoutTicketEscalationDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[ServiceWithoutTicketEscalationDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()