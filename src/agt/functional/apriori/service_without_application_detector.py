"""
Service Without Application Detector - Functional / A Priori

Purpose
-------
This level-1 executor agent detects services that are not linked to any
application module.
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
    ?module a noria:ApplicationModule .
  }
}
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "functional"
    / "apriori"
    / "service_without_application_results.json"
)


def run_query() -> None:
    print(f"[ServiceWithoutApplicationDetector] Querying endpoint: {ENDPOINT}")

    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": QUERY, "format": "application/sparql-results+json"}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", {}).get("bindings", [])

        print(
            f"[ServiceWithoutApplicationDetector] "
            f"{len(results)} service(s) without application found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[ServiceWithoutApplicationDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[ServiceWithoutApplicationDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ServiceWithoutApplicationDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ServiceWithoutApplicationDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()
