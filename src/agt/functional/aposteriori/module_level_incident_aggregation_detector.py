"""
Module Level Incident Aggregation Detector - Functional / A Posteriori

Purpose
-------
This level-1 executor agent detects situations where several technical events
can be aggregated at the application-module level in the NORIA-O knowledge graph.

Business intuition
------------------
In an ICT network, repeated incidents observed on infrastructure resources may
actually reflect a broader functional issue affecting one specific module of an
application.

Even if monitoring records are emitted at resource level, it is useful to
reinterpret them at a higher functional granularity whenever several events
converge towards the same application module.

This may indicate:
- a localized functional degradation inside one application module,
- repeated technical symptoms caused by the same module-level issue,
- or a need to aggregate low-level alerts into a more meaningful diagnosis.

Interest of the query
---------------------
This detector is useful in a posteriori diagnosis because it helps move from
technical event fragmentation to functional aggregation.

It supports:
- alert consolidation,
- incident aggregation,
- reduction of diagnosis noise,
- and improved interpretation of application-level failures.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Functional Alert Consolidation,
- Module Criticality Assessment,
- Repeated Incident Correlation,
- Application Degradation Analysis,
- Root Cause Prioritization.

Output
------
Results are written to:
results/functional/aposteriori/module_level_incident_aggregation_results.json
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

SELECT ?application ?module (COUNT(DISTINCT ?event) AS ?eventCount)
WHERE {
  ?event a noria:EventRecord ;
         noria:logOriginatingManagedObject ?resource .

  ?resource noria:resourceForApplication ?application .

  ?module a noria:ApplicationModule ;
          noria:applicationModuleOf ?application .
}
GROUP BY ?application ?module
HAVING (COUNT(DISTINCT ?event) > 1)
ORDER BY DESC(?eventCount) ?application ?module
"""

# Project root assumed to be MASSYNREAS/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = PROJECT_ROOT / "results" / "functional" / "aposteriori" / "module_level_incident_aggregation_results.json"

# ============================================================
# EXECUTION
# ============================================================

def run_query() -> None:
    """Execute the SPARQL query and store the results."""
    print(f"[ModuleLevelIncidentAggregationDetector] Querying endpoint: {ENDPOINT}")

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
            "[ModuleLevelIncidentAggregationDetector] "
            f"{len(results)} module-level incident aggregation pattern(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[ModuleLevelIncidentAggregationDetector] Results written to '{OUTPUT_FILE}'.")

    except requests.exceptions.ConnectionError:
        print(f"[ModuleLevelIncidentAggregationDetector] ERROR: Cannot connect to {ENDPOINT}", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"[ModuleLevelIncidentAggregationDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[ModuleLevelIncidentAggregationDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()