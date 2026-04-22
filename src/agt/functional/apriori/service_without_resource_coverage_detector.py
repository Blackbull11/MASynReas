"""
Service Without Resource Coverage Detector - Functional / A Priori

Purpose
-------
This level-1 executor agent detects services whose applications do not expose
any visible resource coverage.
"""

import json
import sys
from pathlib import Path

import requests

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX seas: <https://w3id.org/seas/>

SELECT ?service
WHERE {
  ?service a noria:Service .

  FILTER NOT EXISTS {
    ?module seas:subSystemOf ?service .
    ?module noria:applicationModuleOf ?app .
    ?res noria:resourceForApplication ?app .
  }
}
ORDER BY ?service
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "functional"
    / "apriori"
    / "service_without_resource_coverage_results.json"
)


def run_query() -> None:
    print(f"[ServiceWithoutResourceCoverageDetector] Querying endpoint: {ENDPOINT}")

    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": QUERY, "format": "application/sparql-results+json"}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", {}).get("bindings", [])

        print(
            f"[ServiceWithoutResourceCoverageDetector] "
            f"{len(results)} service(s) without resource coverage found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[ServiceWithoutResourceCoverageDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[ServiceWithoutResourceCoverageDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ServiceWithoutResourceCoverageDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ServiceWithoutResourceCoverageDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()
