"""
Structural Fragility Diagnoser - Level 2 / A Priori

Intuition
---------
A structurally fragile resource is one that accumulates multiple independent
governance or topology weaknesses before any incident occurs. A single weakness
(e.g. missing interface) might be acceptable; two or more converging on the same
resource indicate a poorly maintained node that is likely to cause problems or be
very hard to diagnose when an incident eventually occurs.

This agent is purely a priori: it runs on the permanent state of the graph,
independently of any incident context.

Inputs (level-1 results)
------------------------
All files use the `resource` URI as the primary key.

- results/structural/apriori/orphan_resource_results.json
    resource has no parent and no interface — completely isolated
- results/structural/apriori/missing_interface_results.json
    resource has no NetworkInterface — invisible to monitoring
- results/structural/apriori/missing_parent_resource_results.json
    resource has no parent resource — orphaned in the hierarchy
- results/structural/apriori/unmanaged_resource_results.json
    resource has no assigned management system

Correlation key: resource URI

Scoring (number of weakness signals on the same resource)
----------------------------------------------------------
4 signals → confidence 1.0, severity CRITICAL
3 signals → confidence 0.80, severity HIGH
2 signals → confidence 0.55, severity MEDIUM

Output
------
results/level2/apriori/structural_fragility_results.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUTS = {
    "orphan_resource":        PROJECT_ROOT / "results" / "structural" / "apriori" / "orphan_resource_results.json",
    "missing_interface":      PROJECT_ROOT / "results" / "structural" / "apriori" / "missing_interface_results.json",
    "missing_parent_resource":PROJECT_ROOT / "results" / "structural" / "apriori" / "missing_parent_resource_results.json",
    "unmanaged_resource":     PROJECT_ROOT / "results" / "structural" / "apriori" / "unmanaged_resource_results.json",
}

OUTPUT_FILE = PROJECT_ROOT / "results" / "level2" / "apriori" / "structural_fragility_results.json"

SEVERITY_MAP = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM"}
CONFIDENCE_MAP = {4: 1.0, 3: 0.80, 2: 0.55}


def load_resources(path: Path, key: str = "resource") -> set:
    if not path.exists():
        print(f"[StructuralFragility] Input not found (skipped): {path.name}")
        return set()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {row[key]["value"] for row in data if key in row}
    except Exception as e:
        print(f"[StructuralFragility] Could not read {path.name}: {e}", file=sys.stderr)
        return set()


def short_name(uri: str) -> str:
    return uri.split("/")[-1]


def main():
    resource_evidence: defaultdict[str, list[str]] = defaultdict(list)

    for signal_name, path in INPUTS.items():
        for uri in load_resources(path):
            resource_evidence[uri].append(signal_name)

    diagnoses = []
    for uri, evidence in resource_evidence.items():
        count = len(evidence)
        if count < 2:
            continue

        severity   = SEVERITY_MAP.get(count, "MEDIUM")
        confidence = CONFIDENCE_MAP.get(count, 0.55)
        name       = short_name(uri)
        missing    = [s for s in INPUTS if s not in evidence]

        explanation = (
            f"Resource {name} accumulates {count} structural weakness signal(s) "
            f"({', '.join(evidence)}). "
            f"This node is likely poorly governed and will be hard to diagnose under incident conditions."
        )
        if missing:
            explanation += f" Signals not triggered: {', '.join(missing)}."

        diagnoses.append({
            "diagnosis_type": "structural_fragility",
            "mode":           "apriori",
            "target":         uri,
            "target_name":    name,
            "evidence":       evidence,
            "evidence_count": count,
            "confidence":     confidence,
            "severity":       severity,
            "explanation":    explanation,
        })

    diagnoses.sort(key=lambda d: d["evidence_count"], reverse=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(diagnoses, f, indent=2, ensure_ascii=False)

    print(f"[StructuralFragility] {len(diagnoses)} fragile resource(s) identified -> {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
