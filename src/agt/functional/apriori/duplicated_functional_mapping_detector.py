"""
Duplicated Functional Mapping Detector - Functional / A Priori

Purpose
-------
This level-1 executor agent detects resources mapped to several applications,
which may reveal duplicated or ambiguous functional mappings.
"""

import json
import sys
from pathlib import Path

import requests

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>

SELECT ?resource (COUNT(?app) AS ?appCount)
WHERE {
  ?resource noria:resourceForApplication ?app .
}
GROUP BY ?resource
HAVING (COUNT(?app) > 1)
ORDER BY ?resource
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "functional"
    / "apriori"
    / "duplicated_functional_mapping_results.json"
)


def run_query() -> None:
    print(f"[DuplicatedFunctionalMappingDetector] Querying endpoint: {ENDPOINT}")

    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": QUERY, "format": "application/sparql-results+json"}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", {}).get("bindings", [])

        print(
            f"[DuplicatedFunctionalMappingDetector] "
            f"{len(results)} duplicated functional mapping(s) found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[DuplicatedFunctionalMappingDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[DuplicatedFunctionalMappingDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[DuplicatedFunctionalMappingDetector] HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[DuplicatedFunctionalMappingDetector] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_query()
