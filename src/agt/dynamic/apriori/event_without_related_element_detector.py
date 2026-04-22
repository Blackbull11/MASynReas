"""
Event Without Related Element Detector - Dynamic / A Priori

Purpose
-------
This level-1 executor agent detects EventRecord instances in the NORIA-O
knowledge graph that are not linked to any related element.

Business intuition
------------------
An event without a related network element is very difficult to exploit in
dynamic diagnosis.

Without a related element, an event cannot be:
- localized in the network,
- correlated with neighboring events,
- associated with a change or a ticket on the same object,
- or used in propagation, recurrence, or synchronization analyses.

Interest of the query
---------------------
This is a dynamic a priori diagnostic check because it identifies a critical
observability weakness before any dynamic reasoning is attempted.

It is particularly useful because most dynamic a posteriori agents rely on the
presence of noria:eventRelatedElement to connect observed symptoms to the
network structure.

Detection logic
---------------
The query selects every EventRecord for which no noria:eventRelatedElement
value is present in the knowledge graph.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Event Without Timestamp Detector,
- Observability Quality Review,
- Dynamic Diagnosis Reliability Warning.

Output
------
Results are written to:
results/dynamic/apriori/event_without_related_element_results.json
"""

import json
import sys
from pathlib import Path

import requests

ENDPOINT = "http://localhost:8890/sparql"

QUERY = """
PREFIX noria: <https://w3id.org/noria/ontology/>

SELECT ?event
WHERE {
  ?event a noria:EventRecord .
  FILTER NOT EXISTS { ?event noria:eventRelatedElement ?relatedElement . }
}
ORDER BY ?event
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "apriori"
    / "event_without_related_element_results.json"
)


def run_query() -> None:
    print(f"[EventWithoutRelatedElementDetector] Querying endpoint: {ENDPOINT}")

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
            f"[EventWithoutRelatedElementDetector] "
            f"{len(results)} event(s) without related element found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[EventWithoutRelatedElementDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[EventWithoutRelatedElementDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[EventWithoutRelatedElementDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[EventWithoutRelatedElementDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()
