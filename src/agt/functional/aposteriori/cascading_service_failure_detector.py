"""
Cascading Service Failure Detector - Functional / A Posteriori

Purpose
-------
This level-1 executor agent detects situations where a technical incident may
propagate to several services through a shared functional support chain in the
NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, a service failure is often not isolated. A fault affecting a
technical resource may first impact one application, then spread to several
services relying on that same functional component.

In the NORIA-O toy graph, this pattern is approximated as follows:
- an event originates from a resource,
- that resource supports an application,
- one module of that application is attached to more than one service.

This does not fully prove a temporal cascade by itself, but it identifies a
strong structural-functional propagation pattern that is highly relevant in
a posteriori diagnosis.

Interest of the query
---------------------
This detector is useful to identify incidents with potential multi-service
impact. It highlights cases where a single technical fault can affect several
services because they rely on the same application support chain.

Such patterns are important for:
- root cause analysis,
- impact propagation analysis,
- prioritization of incidents,
- and functional dependency interpretation.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Multi-Service Impact Assessment,
- Root Cause Prioritization,
- Shared Dependency Investigation,
- Service Criticality Escalation,
- Functional Propagation Analysis.

Output
------
Results are written to:
results/functional/aposteriori/cascading_service_failure_results.json
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
}
ORDER BY ?time ?event ?service1 ?service2
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "functional" / "aposteriori" / "cascading_service_failure_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[CascadingServiceFailureDetector] Querying endpoint: {ENDPOINT}")

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
            "[CascadingServiceFailureDetector] "
            f"{len(results)} cascading service failure pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[CascadingServiceFailureDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[CascadingServiceFailureDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[CascadingServiceFailureDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[CascadingServiceFailureDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()