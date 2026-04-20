"""
Missing or Incomplete Redundancy Detector - Structural / A Priori

Purpose
-------
This level-1 executor agent detects critical applications whose visible
technical support appears to rely on an insufficient number of supporting
resources in the NORIA-O knowledge graph.

In this first-level template, an application is flagged when:
- it is modeled as an application,
- it is marked as business-critical (or highly critical),
- and it is linked to fewer than two supporting resources.

Business intuition
------------------
In an ICT network, critical services should not rely on a single technical
component whenever redundancy is expected. If a critical application is
supported by only one visible resource, or by no resource at all, this may
indicate:
- an actual single point of failure,
- incomplete redundancy modeling,
- missing infrastructure dependencies,
- or a resilience weakness in the architecture.

Interest of the query
---------------------
This is a structural resilience-oriented sanity check.

It is especially useful in a priori analysis because it helps identify
architectural fragilities before incidents occur. It provides a first-level
warning that a critical application may not have enough visible infrastructure
support to ensure continuity of service.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Application Without Infrastructure Support Detector,
- Resource Mapping Verification,
- Criticality vs Structural Weakness Analysis,
- Infrastructure Dependency Reconstruction,
- Resilience / Failover Verification,
- Data Ingestion Consistency Check.

Output
------
Results are written to:
results/structural/apriori/missing_redundancy_results.json

Important note
--------------
This agent is based on a generic first-level assumption:
a critical application should be supported by at least two distinct resources.

If your graph models redundancy differently (e.g. explicit failover groups,
clusters, standby resources, resilience relations), the query should later
be refined accordingly.
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

SELECT ?application (COUNT(DISTINCT ?resource) AS ?supportCount)
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
GROUP BY ?application
HAVING (COUNT(DISTINCT ?resource) < 2)
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "structural" / "apriori" / "missing_redundancy_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[MissingRedundancyDetector] Querying endpoint: {ENDPOINT}")

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

        print(f"[MissingRedundancyDetector] {len(results)} application(s) with missing or incomplete redundancy found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[MissingRedundancyDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[MissingRedundancyDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[MissingRedundancyDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[MissingRedundancyDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()