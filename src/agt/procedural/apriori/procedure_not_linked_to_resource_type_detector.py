"""
Procedure Not Linked To Resource Type Detector - Procedural / A Priori

Purpose
-------
This level-1 executor agent detects procedures that are not linked to any
resource type in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, an operational procedure is more useful when it is tied
to a class of technical assets or contexts, such as router procedures,
transmission equipment procedures, server procedures, or access network
procedures.

If a procedure exists but is not linked to any resource type, this may indicate:
- overly generic operational knowledge,
- incomplete procedural contextualization,
- difficulty for operators to know when to apply the procedure,
- or incomplete linkage between remediation knowledge and infrastructure modeling.

Interest of the query
---------------------
This is a core procedural preparedness check at the interface between
operational knowledge and the technical layer.

It is especially useful in a priori analysis because it highlights procedures
that are present in the knowledge graph but are not grounded in any explicit
resource category. In real operations, such procedures are harder to select,
reuse, automate, or recommend reliably.

Operational modeling choice
---------------------------
NORIA-O does not expose a simple direct predicate such as
"procedureAppliesToResourceType". Therefore, in this detector, a procedure is
considered linked to a resource type if there exists at least one EventRecord
that:
- recommends the procedure via noria:alarmProposedRepairAction, and
- is related to a Resource carrying a noria:resourceType.

This operationalization is consistent with the ontology, where:
- noria:alarmProposedRepairAction has range pep:Procedure, and
- noria:resourceType is defined on noria:Resource.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Procedure Contextualization Completeness Check,
- Incident Playbook Precision Analysis,
- Event-to-Procedure Mapping Review,
- Resource-Specific Remediation Coverage Check,
- Operational Knowledge Formalization Review.

Output
------
Results are written to:
results/procedural/apriori/procedure_not_linked_to_resource_type_results.json
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
PREFIX pep: <https://w3id.org/pep/>

SELECT DISTINCT ?procedure
WHERE {
  ?procedure a pep:Procedure .

  FILTER NOT EXISTS {
    ?event a noria:EventRecord ;
           noria:alarmProposedRepairAction ?procedure ;
           noria:eventRelatedElement ?resource .

    ?resource a noria:Resource ;
              noria:resourceType ?resourceType .
  }
}
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "procedural" / "apriori" / "procedure_not_linked_to_resource_type_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ProcedureNotLinkedToResourceTypeDetector] Querying endpoint: {ENDPOINT}")

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

        print(f"[ProcedureNotLinkedToResourceTypeDetector] {len(results)} procedure(s) without linked resource type found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[ProcedureNotLinkedToResourceTypeDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[ProcedureNotLinkedToResourceTypeDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[ProcedureNotLinkedToResourceTypeDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[ProcedureNotLinkedToResourceTypeDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()