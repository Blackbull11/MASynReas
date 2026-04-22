"""
Event Without Timestamp Detector - Dynamic / A Priori

Purpose
-------
This level-1 executor agent detects EventRecord instances in the NORIA-O
knowledge graph that do not have any logging timestamp.

Business intuition
------------------
A timestamp is the minimum information required to reason about the temporal
behavior of an event.

Without a logging time, an event cannot be:
- ordered with respect to other events,
- correlated with a change or a ticket,
- used in burst or recurrence analysis,
- or integrated into any dynamic diagnosis pipeline.

Interest of the query
---------------------
This is a dynamic a priori diagnostic check because it identifies a crucial
observability weakness before any temporal analysis is attempted.

It is particularly useful because missing timestamps make most dynamic
a posteriori agents unreliable or unusable.

Detection logic
---------------
The query selects every EventRecord for which no noria:loggingTime value is
present in the knowledge graph.

Potential follow-up diagnostics
-------------------------------
If this pattern is detected, the MAS may trigger:
- Event Without Related Element Detector,
- Observability Quality Review,
- Dynamic Diagnosis Reliability Warning.

Output
------
Results are written to:
results/dynamic/apriori/event_without_timestamp_results.json
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
  FILTER NOT EXISTS { ?event noria:loggingTime ?loggingTime . }
}
ORDER BY ?event
"""

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "dynamic"
    / "apriori"
    / "event_without_timestamp_results.json"
)


def run_query() -> None:
    print(f"[EventWithoutTimestampDetector] Querying endpoint: {ENDPOINT}")

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
            f"[EventWithoutTimestampDetector] "
            f"{len(results)} event(s) without timestamp found."
        )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(
            f"[EventWithoutTimestampDetector] "
            f"Results written to '{OUTPUT_FILE}'."
        )

    except requests.exceptions.ConnectionError:
        print(
            f"[EventWithoutTimestampDetector] ERROR: Cannot connect to {ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(
            f"[EventWithoutTimestampDetector] HTTP Error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(
            f"[EventWithoutTimestampDetector] Unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_query()
