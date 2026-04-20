"""
Criticality vs Structural Weakness Detector - Structural / A Priori

Purpose
-------
This level-1 executor agent detects applications whose business criticality
appears inconsistent with the weakness of their visible technical support
in the NORIA-O knowledge graph.

In this first-level implementation, an application is flagged when:
- it is modeled as an application,
- it is marked as critical or highly critical,
- and it has either no supporting resource or fewer than two supporting resources.

Business intuition
------------------
In an ICT network, highly critical applications should normally rely on a
technical structure that is strong enough to support service continuity.
If a business-critical application is supported by too few visible resources,
this may reveal:
- a single point of failure,
- incomplete infrastructure mapping,
- weak resilience design,
- or an inconsistency between business importance and technical deployment.

Interest of the query
---------------------
This is a structural risk-oriented consistency check linking the business layer
to the infrastructure layer.

It is especially useful in a priori analysis because it helps identify
architectural weaknesses before any incident occurs. It acts as an early warning
that the graph exposes an insufficient technical basis for a critical service.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Application Without Infrastructure Support Detector,
- Missing or Incomplete Redundancy Detector,
- Resource Mapping Verification,
- Critical Application Dependency Reconstruction,
- Resilience / Failover Verification,
- Data Ingestion Consistency Check.

Output
------
Results are written to:
results/structural/apriori/criticality_structural_weakness_results.json

Important note
--------------
This first-level agent intentionally uses a simple structural weakness proxy:
the number of distinct supporting resources linked to an application.

If your graph later exposes richer resilience information (clusters, failover
groups, standby paths, service chains, etc.), the query should be refined.
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

SELECT ?application ?criticality (COUNT(DISTINCT ?resource) AS ?supportCount)
WHERE {
  ?application a noria:Application ;
               noria:businessCriticality ?criticality .

  FILTER (
    ?criticality = <https://w3id.org/noria/kos/application/criticality/critical> ||
    ?criticality = <https://w3id.org/noria/kos/application/criticality/high-critical>
  )

  OPTIONAL {
    ?resource noria:resourceForApplication ?application .
  }
}
GROUP BY ?application ?criticality
HAVING (COUNT(DISTINCT ?resource) < 2)
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "structural" / "apriori" / "criticality_structural_weakness_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[CriticalityStructuralWeaknessDetector] Querying endpoint: {ENDPOINT}")

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
            "[CriticalityStructuralWeaknessDetector] "
            f"{len(results)} critical application(s) with structural weakness found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            "[CriticalityStructuralWeaknessDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[CriticalityStructuralWeaknessDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[CriticalityStructuralWeaknessDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[CriticalityStructuralWeaknessDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()