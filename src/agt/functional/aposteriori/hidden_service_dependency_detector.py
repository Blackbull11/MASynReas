"""
Hidden Service Dependency Detector - Functional / A Posteriori

Purpose
-------
This level-1 executor agent detects situations where several services may be
implicitly dependent on the same technical and functional support chain in the
NORIA-O knowledge graph, without any explicit dependency relation between them.

Business intuition
------------------
In an ICT network, two services may appear independent from a modeling point of
view, while in practice they rely on the same application component or the same
technical support resource.

When a technical incident affects such a shared support chain, several services
may be impacted simultaneously even though no explicit dependency between them
is represented in the knowledge graph.

This may indicate:
- a hidden functional dependency,
- an incomplete service dependency model,
- an undocumented shared support component,
- or a structural blind spot in the graph.

Interest of the query
---------------------
This detector is useful in a posteriori diagnosis because it highlights service
co-impact patterns that are not explained by the explicit service structure.

It helps:
- reveal implicit dependencies,
- explain correlated service failures,
- improve impact analysis,
- and identify missing knowledge in the graph.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Service Dependency Enrichment,
- Multi-Service Impact Analysis,
- Shared Support Chain Investigation,
- Root Cause Prioritization,
- Functional Topology Completion Check.

Output
------
Results are written to:
results/functional/aposteriori/hidden_service_dependency_results.json
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

SELECT DISTINCT ?event ?time ?resource ?application ?module ?service1 ?service2
WHERE {
  ?event a noria:EventRecord ;
         noria:loggingTime ?time ;
         noria:logOriginatingManagedObject ?resource .

  ?resource noria:resourceForApplication ?application .

  ?module a noria:ApplicationModule ;
          noria:applicationModuleOf ?application ;
          seas:subSystemOf ?service1, ?service2 .

  ?service1 a noria:Service .
  ?service2 a noria:Service .

  FILTER (?service1 != ?service2)

  FILTER NOT EXISTS { ?service1 seas:subSystemOf ?service2 . }
  FILTER NOT EXISTS { ?service2 seas:subSystemOf ?service1 . }
}
ORDER BY ?time ?event ?service1 ?service2
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "functional" / "aposteriori" / "hidden_service_dependency_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[HiddenServiceDependencyDetector] Querying endpoint: {ENDPOINT}")

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
            "[HiddenServiceDependencyDetector] "
            f"{len(results)} hidden service dependency pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[HiddenServiceDependencyDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[HiddenServiceDependencyDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[HiddenServiceDependencyDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[HiddenServiceDependencyDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()
