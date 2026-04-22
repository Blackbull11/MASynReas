"""
Inconsistent Service Hierarchy Detector - Functional / A Priori

Purpose
-------
This level-1 executor agent detects modules linked to several parent
services, which may indicate an inconsistent service hierarchy.
"""

import json
import sys
from pathlib import Path

import requests

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX seas: <https://w3id.org/seas/>

SELECT ?module (COUNT(?service) AS ?serviceCount)
WHERE {
  ?module a noria:ApplicationModule .
  ?module seas:subSystemOf ?service .
}
GROUP BY ?module
HAVING (COUNT(?service) > 1)
ORDER BY ?module
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "functional"
    / "apriori"
    / "inconsistent_service_hierarchy_results.json"
)


def run_query() -> None:
    print(f"[InconsistentServiceHierarchyDetector] Querying endpoint: {ENDPOINT}")

    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": QUERY, "format": "application/sparql-results+json"}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", {}).get("bindings", [])

        print(
            f"[InconsistentServiceHierarchyDetector] "
            f"{len(results)} inconsistent service hierarchy case(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[InconsistentServiceHierarchyDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[InconsistentServiceHierarchyDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[InconsistentServiceHierarchyDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[InconsistentServiceHierarchyDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()
