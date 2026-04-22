"""
Single Point of Failure Diagnoser - Level 2 / A Posteriori

Intuition
---------
A resource is a single point of failure when it combines several structural
weaknesses simultaneously: it is weakly connected (isolated), has no backup
(no redundancy), and supports many dependents (high impact).
Level-1 detectors each catch one of these signals in isolation.
This agent correlates them on the same resource URI to produce a unified diagnosis.

Inputs (level-1 results)
------------------------
- results/structural/aposteriori/isolated_incident_resource_results.json
    resource appears with low connectivity during an incident
- results/structural/aposteriori/no_redundancy_incident_results.json
    resource has no redundant counterpart during an incident
- results/structural/aposteriori/high_impact_resource_results.json
    resource supports many applications or dependents

Correlation key: resource URI (present in all three files)

Scoring
-------
Evidence count | Confidence | Severity
3 of 3         | 1.0        | CRITICAL
2 of 3         | 0.65       | HIGH

Output
------
results/level2/aposteriori/single_point_of_failure_results.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUTS = {
    "isolated_incident_resource": PROJECT_ROOT / "results" / "structural" / "aposteriori" / "isolated_incident_resource_results.json",
    "no_redundancy_incident":     PROJECT_ROOT / "results" / "structural" / "aposteriori" / "no_redundancy_incident_results.json",
    "high_impact_resource":       PROJECT_ROOT / "results" / "structural" / "aposteriori" / "high_impact_resource_results.json",
}

OUTPUT_FILE = PROJECT_ROOT / "results" / "level2" / "aposteriori" / "single_point_of_failure_results.json"

WEIGHTS = {
    "isolated_incident_resource": 1,
    "no_redundancy_incident":     1,
    "high_impact_resource":       1,
}


def load_resources(path: Path) -> set:
    """Extract resource URIs from a SPARQL result JSON file."""
    if not path.exists():
        print(f"[SPOF] Input not found (skipped): {path.name}")
        return set()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {row["resource"]["value"] for row in data if "resource" in row}
    except Exception as e:
        print(f"[SPOF] Could not read {path.name}: {e}", file=sys.stderr)
        return set()


def short_name(uri: str) -> str:
    return uri.split("/")[-1]


def main():
    resource_evidence: defaultdict[str, list[str]] = defaultdict(list)

    for signal_name, path in INPUTS.items():
        for resource_uri in load_resources(path):
            resource_evidence[resource_uri].append(signal_name)

    diagnoses = []
    for resource_uri, evidence in resource_evidence.items():
        count = len(evidence)
        if count < 2:
            continue

        confidence = 1.0 if count == 3 else 0.65
        severity   = "CRITICAL" if count == 3 else "HIGH"
        name       = short_name(resource_uri)

        missing = [s for s in INPUTS if s not in evidence]
        explanation = (
            f"Resource {name} is confirmed as a single point of failure: "
            f"corroborated by {count} independent structural signals "
            f"({', '.join(evidence)})."
        )
        if missing:
            explanation += f" Signal(s) absent: {', '.join(missing)}."

        diagnoses.append({
            "diagnosis_type":  "single_point_of_failure",
            "mode":            "aposteriori",
            "target":          resource_uri,
            "target_name":     name,
            "evidence":        evidence,
            "evidence_count":  count,
            "confidence":      confidence,
            "severity":        severity,
            "explanation":     explanation,
        })

    diagnoses.sort(key=lambda d: d["evidence_count"], reverse=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(diagnoses, f, indent=2, ensure_ascii=False)

    print(f"[SPOF] {len(diagnoses)} single-point-of-failure diagnosis(es) written to {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
