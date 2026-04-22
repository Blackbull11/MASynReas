"""
Change-Induced Incident Diagnoser - Level 2 / A Posteriori

Intuition
---------
A change request is the likely root cause of an incident when two independent
signals converge: a temporal signal (a change was followed by an incident on a
related element shortly after) and a procedural signal (the same change is linked
to multiple incident tickets). Each signal alone is weak; together they constitute
strong evidence of a faulty or poorly planned change rollout.

Inputs (level-1 results)
------------------------
- results/dynamic/aposteriori/change_followed_by_incident_results.json
    fields: change, event, relatedElement
    a change was temporally followed by an event on a related resource
- results/procedural/aposteriori/change_linked_to_multiple_incidents_results.json
    fields: change, incidentCount
    a change request is associated with several distinct incident tickets

Correlation key: change URI

Scoring
-------
Corroborated by both signals → confidence 0.85, severity HIGH
Only procedural signal (multiple incidents, no temporal link) → confidence 0.55, severity MEDIUM
Only temporal signal → confidence 0.45, severity MEDIUM

Output
------
results/level2/aposteriori/change_induced_incident_results.json
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_TEMPORAL   = PROJECT_ROOT / "results" / "dynamic"    / "aposteriori" / "change_followed_by_incident_results.json"
INPUT_PROCEDURAL = PROJECT_ROOT / "results" / "procedural" / "aposteriori" / "change_linked_to_multiple_incidents_results.json"
OUTPUT_FILE      = PROJECT_ROOT / "results" / "level2"     / "aposteriori" / "change_induced_incident_results.json"


def load_changes_temporal(path: Path) -> dict:
    """Returns {change_uri: [relatedElement, ...]}"""
    if not path.exists():
        print(f"[ChangeInduced] Input not found (skipped): {path.name}")
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        result = {}
        for row in data:
            if "change" not in row:
                continue
            uri = row["change"]["value"]
            elem = row.get("relatedElement", {}).get("value", "")
            result.setdefault(uri, [])
            if elem and elem not in result[uri]:
                result[uri].append(elem)
        return result
    except Exception as e:
        print(f"[ChangeInduced] Could not read {path.name}: {e}", file=sys.stderr)
        return {}


def load_changes_procedural(path: Path) -> dict:
    """Returns {change_uri: incident_count}"""
    if not path.exists():
        print(f"[ChangeInduced] Input not found (skipped): {path.name}")
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {
            row["change"]["value"]: int(row.get("incidentCount", {}).get("value", 1))
            for row in data if "change" in row
        }
    except Exception as e:
        print(f"[ChangeInduced] Could not read {path.name}: {e}", file=sys.stderr)
        return {}


def short_name(uri: str) -> str:
    return uri.split("/")[-1]


def main():
    temporal   = load_changes_temporal(INPUT_TEMPORAL)
    procedural = load_changes_procedural(INPUT_PROCEDURAL)

    all_changes = set(temporal) | set(procedural)
    diagnoses = []

    for change_uri in all_changes:
        has_temporal   = change_uri in temporal
        has_procedural = change_uri in procedural
        name           = short_name(change_uri)

        evidence = []
        if has_temporal:
            evidence.append("change_followed_by_incident")
        if has_procedural:
            evidence.append("change_linked_to_multiple_incidents")

        if has_temporal and has_procedural:
            confidence  = 0.85
            severity    = "HIGH"
            incident_n  = procedural[change_uri]
            explanation = (
                f"Change {name} is the probable root cause: it was temporally "
                f"followed by an incident on a related element AND is linked to "
                f"{incident_n} incident ticket(s). Dual corroboration (dynamic + procedural)."
            )
        elif has_procedural:
            confidence  = 0.55
            severity    = "MEDIUM"
            incident_n  = procedural[change_uri]
            explanation = (
                f"Change {name} is linked to {incident_n} incident ticket(s) "
                f"but no temporal proximity signal was detected. Moderate suspicion."
            )
        else:
            confidence  = 0.45
            severity    = "MEDIUM"
            explanation = (
                f"Change {name} was temporally followed by an incident, "
                f"but no multi-incident procedural link was found. Weak suspicion."
            )

        diagnoses.append({
            "diagnosis_type": "change_induced_incident",
            "mode":           "aposteriori",
            "target":         change_uri,
            "target_name":    name,
            "evidence":       evidence,
            "confidence":     confidence,
            "severity":       severity,
            "explanation":    explanation,
        })

    diagnoses.sort(key=lambda d: d["confidence"], reverse=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(diagnoses, f, indent=2, ensure_ascii=False)

    print(f"[ChangeInduced] {len(diagnoses)} change-induced diagnosis(es) written to {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
