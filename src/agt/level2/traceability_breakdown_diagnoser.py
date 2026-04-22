"""
Traceability Breakdown Diagnoser - Level 2 / A Posteriori

Intuition
---------
A healthy operational process requires a complete traceability chain:
every incident event should produce a ticket, and every ticket should
reference its triggering event. When both links are broken simultaneously,
the operations team has lost full visibility: incidents occur without
documentation, and tickets exist without traceable causes.
This is a systemic process failure, not a one-off oversight.

Inputs (level-1 results)
------------------------
- results/procedural/aposteriori/incident_without_ticket_results.json
    fields: event, severity, time, relatedElement
    incident events that have no associated TroubleTicket
- results/procedural/aposteriori/ticket_without_linked_event_results.json
    fields: ticket, status, creationDate
    TroubleTickets that have no linked EventRecord

These two files track opposite ends of the same broken chain.
They cannot be joined on a common key; their co-presence is the signal.

Scoring
-------
Both files non-empty  → confidence 0.90, severity HIGH   (systemic breakdown)
Only incidents without tickets → confidence 0.60, severity MEDIUM (missing ticketing)
Only tickets without events    → confidence 0.55, severity MEDIUM (orphan tickets)

Output
------
results/level2/aposteriori/traceability_breakdown_results.json
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_INCIDENTS = PROJECT_ROOT / "results" / "procedural" / "aposteriori" / "incident_without_ticket_results.json"
INPUT_TICKETS   = PROJECT_ROOT / "results" / "procedural" / "aposteriori" / "ticket_without_linked_event_results.json"
OUTPUT_FILE     = PROJECT_ROOT / "results" / "level2" / "aposteriori" / "traceability_breakdown_results.json"


def load_file(path: Path) -> list:
    if not path.exists():
        print(f"[Traceability] Input not found (skipped): {path.name}")
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Traceability] Could not read {path.name}: {e}", file=sys.stderr)
        return []


def main():
    incidents = load_file(INPUT_INCIDENTS)
    tickets   = load_file(INPUT_TICKETS)

    n_incidents = len(incidents)
    n_tickets   = len(tickets)

    if n_incidents == 0 and n_tickets == 0:
        print("[Traceability] No traceability issues detected.")
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        return

    evidence = []
    if n_incidents > 0:
        evidence.append("incident_without_ticket")
    if n_tickets > 0:
        evidence.append("ticket_without_linked_event")

    if n_incidents > 0 and n_tickets > 0:
        confidence  = 0.90
        severity    = "HIGH"
        explanation = (
            f"Systemic traceability breakdown: {n_incidents} incident event(s) have no "
            f"associated ticket, AND {n_tickets} ticket(s) have no linked event. "
            f"Both ends of the traceability chain are broken simultaneously."
        )
    elif n_incidents > 0:
        confidence  = 0.60
        severity    = "MEDIUM"
        explanation = (
            f"{n_incidents} incident event(s) occurred without generating a TroubleTicket. "
            f"These incidents are undocumented and cannot be tracked or escalated."
        )
    else:
        confidence  = 0.55
        severity    = "MEDIUM"
        explanation = (
            f"{n_tickets} TroubleTicket(s) exist without any linked EventRecord. "
            f"These tickets cannot be traced back to an observable cause."
        )

    diagnosis = [{
        "diagnosis_type":         "traceability_breakdown",
        "mode":                   "aposteriori",
        "target":                 "operational_process",
        "evidence":               evidence,
        "unlinked_incident_count": n_incidents,
        "unlinked_ticket_count":   n_tickets,
        "confidence":             confidence,
        "severity":               severity,
        "explanation":            explanation,
        "sample_incidents":       [r.get("event", {}).get("value", "") for r in incidents[:3]],
        "sample_tickets":         [r.get("ticket", {}).get("value", "") for r in tickets[:3]],
    }]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(diagnosis, f, indent=2, ensure_ascii=False)

    print(f"[Traceability] Diagnosis written to {OUTPUT_FILE.name} — severity: {severity}")


if __name__ == "__main__":
    main()
