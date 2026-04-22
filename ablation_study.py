"""
ablation_study.py - PSC INF12

Compares 3 conditions on the same diagnostic scenarios to measure
the added value of each MAS layer on LLM output quality.

Conditions
----------
A - LLM alone     : only the trouble ticket text (what a human operator sees)
B - Level-1 -> LLM: structured JSON facts from 54 level-1 detector agents
C - Level-1+2->LLM: level-1 facts + level-2 correlation diagnoses

Metrics (per condition, per scenario)
--------------------------------------
1. hallucination_rate  : fraction of entity names in LLM output not in known entities
2. conformity_score    : fraction of ground-truth entities mentioned in LLM output
3. consistency_score   : semantic similarity across N_RUNS (1.0 = identical diagnoses)
4. severity_match      : 1 if diagnosed severity matches ground truth, else 0

Usage
-----
  python -X utf8 ablation_study.py
Requires Ollama running on localhost:11434 with llama3.2:3b and llama3.1:8b pulled.
"""

import json
import re
import time
from pathlib import Path
from datetime import datetime

import requests

# ── Configuration ─────────────────────────────────────────────────────────────
OLLAMA_URL     = "http://localhost:11434/api/generate"
MODEL_ABLATION = "llama3.1:8b"   # reasoning tasks (ablation)
MODEL_NARRATIVE= "llama3.2:3b"   # narrative synthesis (level 3, kept small)
N_RUNS         = 5               # runs per condition for consistency measurement
OUTPUT_FILE    = "ablation_results.json"
PROJECT_ROOT   = Path(__file__).resolve().parent

# ── Scenarios with ground truth ───────────────────────────────────────────────
# Each scenario defines:
#   ticket_text    : what Condition A receives (minimal operator context)
#   level1_facts   : what Condition B receives (structured level-1 JSON outputs)
#   level2_diagnoses: what Condition C adds on top (level-2 correlation results)
#   ground_truth   : expected diagnosis type, target entity, severity
#   known_entities : all entities that legitimately exist in this scenario

SCENARIOS = [
    {
        "id": "S1_single_point_of_failure",
        "description": "Resource RES_TOY_as2 triggers 3 independent structural signals",
        "ground_truth": {
            "diagnosis_type": "single_point_of_failure",
            "target":         "RES_TOY_as2",
            "severity":       "CRITICAL",
        },
        "known_entities": ["RES_TOY_as2", "RES_TOY_srv1", "APP_TOY_PFS01", "TT_TOY2022TT"],

        "ticket_text": (
            "Ticket TT_TOY2022TT — Resource RES_TOY_as2 is involved in an active incident. "
            "The resource appears to have limited network connectivity and no backup system. "
            "Multiple downstream applications may be affected."
        ),

        "level1_facts": {
            "isolated_incident_resource": [
                {"resource": "RES_TOY_as2", "ticket": "TT_TOY2022TT", "connectivityDegree": "1"}
            ],
            "no_redundancy_incident": [
                {"resource": "RES_TOY_as2", "ticket": "TT_TOY2022TT"},
                {"resource": "RES_TOY_srv1", "ticket": "TT_TOY2022TT"},
            ],
            "high_impact_resource": [
                {"resource": "RES_TOY_as2", "ticket": "TT_TOY2022TT"}
            ],
        },

        "level2_diagnoses": [
            {
                "diagnosis_type": "single_point_of_failure",
                "target_name":    "RES_TOY_as2",
                "evidence":       ["isolated_incident_resource", "no_redundancy_incident", "high_impact_resource"],
                "evidence_count": 3,
                "confidence":     1.0,
                "severity":       "CRITICAL",
                "explanation": (
                    "Resource RES_TOY_as2 is confirmed as a single point of failure: "
                    "corroborated by 3 independent structural signals. "
                    "It is weakly connected, has no redundant counterpart, and supports multiple dependents."
                ),
            }
        ],
    },

    {
        "id": "S2_change_induced_incident",
        "description": "Change CR_2022_001 corroborated by dynamic and procedural signals",
        "ground_truth": {
            "diagnosis_type": "change_induced_incident",
            "target":         "CR_2022_001",
            "severity":       "HIGH",
        },
        "known_entities": ["CR_2022_001", "RES_TOY_as2", "EV_as2_alarm", "TT_TOY2022TT"],

        "ticket_text": (
            "Ticket TT_TOY2022TT — An incident was detected on RES_TOY_as2 shortly after "
            "a maintenance change was applied on the network. The change reference is CR_2022_001. "
            "This change has been associated with multiple recent incident reports."
        ),

        "level1_facts": {
            "change_followed_by_incident": [
                {"change": "CR_2022_001", "event": "EV_as2_alarm", "relatedElement": "RES_TOY_as2"}
            ],
            "change_linked_to_multiple_incidents": [
                {"change": "CR_2022_001", "incidentCount": "3"}
            ],
        },

        "level2_diagnoses": [
            {
                "diagnosis_type": "change_induced_incident",
                "target_name":    "CR_2022_001",
                "evidence":       ["change_followed_by_incident", "change_linked_to_multiple_incidents"],
                "confidence":     0.85,
                "severity":       "HIGH",
                "explanation": (
                    "Change CR_2022_001 is the probable root cause: it was temporally followed "
                    "by an incident on RES_TOY_as2 AND is linked to 3 incident tickets. "
                    "Dual corroboration from dynamic and procedural families."
                ),
            }
        ],
    },

    {
        "id": "S3_traceability_breakdown",
        "description": "Incidents without tickets and tickets without events co-present",
        "ground_truth": {
            "diagnosis_type": "traceability_breakdown",
            "target":         "operational_process",
            "severity":       "HIGH",
        },
        "known_entities": ["EV_ORPHAN_1", "EV_ORPHAN_2", "TT_ORPHAN_1"],

        "ticket_text": (
            "Operations review flagged anomalies in the ticketing process. "
            "Several alarm events were recorded in the monitoring system but no corresponding "
            "trouble tickets were opened. Separately, some tickets exist in the system with "
            "no traceable triggering event."
        ),

        "level1_facts": {
            "incident_without_ticket": [
                {"event": "EV_ORPHAN_1", "severity": "major"},
                {"event": "EV_ORPHAN_2", "severity": "minor"},
            ],
            "ticket_without_linked_event": [
                {"ticket": "TT_ORPHAN_1", "status": "open"}
            ],
        },

        "level2_diagnoses": [
            {
                "diagnosis_type":          "traceability_breakdown",
                "target":                  "operational_process",
                "evidence":                ["incident_without_ticket", "ticket_without_linked_event"],
                "unlinked_incident_count": 2,
                "unlinked_ticket_count":   1,
                "confidence":              0.90,
                "severity":                "HIGH",
                "explanation": (
                    "Systemic traceability breakdown: 2 incident events have no associated ticket "
                    "AND 1 ticket has no linked event. Both ends of the traceability chain are broken."
                ),
            }
        ],
    },

    # ── S4 : apriori structural fragility ────────────────────────────────────
    {
        "id": "S4_structural_fragility_apriori",
        "description": "RES_TOY_as2 accumulates 3 apriori governance weaknesses before any incident",
        "ground_truth": {
            "diagnosis_type": "structural_fragility",
            "target":         "RES_TOY_as2",
            "severity":       "HIGH",
        },
        "known_entities": ["RES_TOY_as2", "RES_TOY_srv1"],

        "ticket_text": (
            "Routine infrastructure audit — no active incident. "
            "Resource RES_TOY_as2 was flagged during inventory review: "
            "it has no parent resource in the hierarchy, no network interface recorded, "
            "and no management system assigned. It appears completely unmanaged."
        ),

        "level1_facts": {
            "orphan_resource": [
                {"resource": "RES_TOY_as2"},
                {"resource": "RES_TOY_srv1"},
            ],
            "missing_interface": [
                {"resource": "RES_TOY_as2"},
                {"resource": "RES_TOY_srv1"},
            ],
            "missing_parent_resource": [
                {"resource": "RES_TOY_as2"}
            ],
            "unmanaged_resource": [],
        },

        "level2_diagnoses": [
            {
                "diagnosis_type": "structural_fragility",
                "mode":           "apriori",
                "target_name":    "RES_TOY_as2",
                "evidence":       ["orphan_resource", "missing_interface", "missing_parent_resource"],
                "evidence_count": 3,
                "confidence":     0.80,
                "severity":       "HIGH",
                "explanation": (
                    "Resource RES_TOY_as2 accumulates 3 structural weakness signals "
                    "(orphan_resource, missing_interface, missing_parent_resource). "
                    "This node is poorly governed and will be hard to diagnose when an incident occurs."
                ),
            },
            {
                "diagnosis_type": "structural_fragility",
                "mode":           "apriori",
                "target_name":    "RES_TOY_srv1",
                "evidence":       ["orphan_resource", "missing_interface"],
                "evidence_count": 2,
                "confidence":     0.55,
                "severity":       "MEDIUM",
                "explanation": (
                    "Resource RES_TOY_srv1 shows 2 structural weakness signals "
                    "(orphan_resource, missing_interface). Moderate governance concern."
                ),
            },
        ],
    },

    # ── S5 : cross-family — structural + dynamic + procedural ────────────────
    {
        "id": "S5_cross_family_combined",
        "description": "RES_TOY_as2 is a SPOF AND the incident was likely change-induced",
        "ground_truth": {
            "diagnosis_type": "single_point_of_failure",   # primary (most critical)
            "target":         "RES_TOY_as2",
            "severity":       "CRITICAL",
        },
        "known_entities": [
            "RES_TOY_as2", "RES_TOY_srv1", "CR_2022_001",
            "EV_as2_alarm", "TT_TOY2022TT", "APP_TOY_PFS01",
        ],

        "ticket_text": (
            "Critical incident on RES_TOY_as2 — ticket TT_TOY2022TT. "
            "The resource is involved in a major alarm. A maintenance change CR_2022_001 "
            "was applied two hours before the incident. The resource has limited connectivity "
            "and no backup system. Multiple applications are reported as impacted."
        ),

        "level1_facts": {
            "isolated_incident_resource": [
                {"resource": "RES_TOY_as2", "ticket": "TT_TOY2022TT", "connectivityDegree": "1"}
            ],
            "no_redundancy_incident": [
                {"resource": "RES_TOY_as2", "ticket": "TT_TOY2022TT"}
            ],
            "high_impact_resource": [
                {"resource": "RES_TOY_as2", "ticket": "TT_TOY2022TT"}
            ],
            "change_followed_by_incident": [
                {"change": "CR_2022_001", "event": "EV_as2_alarm", "relatedElement": "RES_TOY_as2"}
            ],
            "change_linked_to_multiple_incidents": [
                {"change": "CR_2022_001", "incidentCount": "3"}
            ],
        },

        "level2_diagnoses": [
            {
                "diagnosis_type": "single_point_of_failure",
                "target_name":    "RES_TOY_as2",
                "evidence":       ["isolated_incident_resource", "no_redundancy_incident", "high_impact_resource"],
                "confidence":     1.0,
                "severity":       "CRITICAL",
                "explanation": (
                    "RES_TOY_as2 is a single point of failure: isolated, non-redundant, high-impact. "
                    "Immediate action required."
                ),
            },
            {
                "diagnosis_type": "change_induced_incident",
                "target_name":    "CR_2022_001",
                "evidence":       ["change_followed_by_incident", "change_linked_to_multiple_incidents"],
                "confidence":     0.85,
                "severity":       "HIGH",
                "explanation": (
                    "Change CR_2022_001 is the probable trigger: temporal and procedural corroboration. "
                    "Consider rolling back CR_2022_001 while restoring RES_TOY_as2."
                ),
            },
        ],
    },
]

# ── Prompt builders ───────────────────────────────────────────────────────────

def build_prompt_A(scenario: dict) -> str:
    return (
        "You are a network operations expert. Based only on the following trouble ticket, "
        "provide a concise diagnosis: identify the most likely root cause, the affected entity, "
        "and the severity level (CRITICAL / HIGH / MEDIUM / LOW).\n\n"
        f"TICKET:\n{scenario['ticket_text']}\n\n"
        "Answer in 3-5 sentences. Be specific about entity names and severity."
    )

def build_prompt_B(scenario: dict) -> str:
    facts_text = json.dumps(scenario["level1_facts"], indent=2)
    return (
        "You are a network operations expert. The following structured facts were automatically "
        "extracted from a knowledge graph by specialized detector agents. "
        "Based on these facts, provide a concise diagnosis: identify the most likely root cause, "
        "the affected entity, and the severity level (CRITICAL / HIGH / MEDIUM / LOW).\n\n"
        f"DETECTOR RESULTS:\n{facts_text}\n\n"
        "Answer in 3-5 sentences. Be specific about entity names and severity."
    )

def build_prompt_C(scenario: dict) -> str:
    facts_text = json.dumps(scenario["level1_facts"], indent=2)
    diag_text  = json.dumps(scenario["level2_diagnoses"], indent=2)
    return (
        "You are a network operations expert. The following structured facts were extracted "
        "from a knowledge graph by detector agents, and then correlated by diagnosis agents "
        "that identified higher-level patterns. "
        "Based on these inputs, provide a concise diagnosis: confirm or nuance the suggested "
        "diagnosis, and state the severity level (CRITICAL / HIGH / MEDIUM / LOW).\n\n"
        f"DETECTOR RESULTS:\n{facts_text}\n\n"
        f"CORRELATION DIAGNOSES:\n{diag_text}\n\n"
        "Answer in 3-5 sentences. Be specific about entity names and severity."
    )

# ── LLM call ─────────────────────────────────────────────────────────────────

def call_llm(prompt: str, model: str) -> tuple[str, float]:
    t0 = time.perf_counter()
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model":  model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300},
        }, timeout=120)
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
    except Exception as e:
        text = f"[ERROR: {e}]"
    elapsed = (time.perf_counter() - t0) * 1000
    return text, elapsed

# ── Metrics ───────────────────────────────────────────────────────────────────

def extract_words(text: str) -> set:
    return set(re.findall(r"[A-Za-z0-9_]+", text))

def hallucination_rate(response: str, known_entities: list) -> float:
    """
    Fraction of capitalized tokens in the response that look like entity names
    but are not in the known entity set. Heuristic: tokens matching the
    NORIA naming pattern (all-caps segments with underscores, e.g. RES_TOY_as2).
    """
    candidates = set(re.findall(r"\b[A-Z]{2,}[_A-Za-z0-9]*\b", response))
    candidates -= {"CRITICAL","HIGH","MEDIUM","LOW","LLM","MAS","RDF","JSON","AND","OR","NOT","IF"}
    if not candidates:
        return 0.0
    hallucinated = [c for c in candidates if not any(e.upper() in c.upper() or c.upper() in e.upper() for e in known_entities)]
    return round(len(hallucinated) / len(candidates), 2)

def conformity_score(response: str, ground_truth: dict) -> float:
    """Fraction of ground-truth fields whose value appears in the response."""
    hits = 0
    checks = [ground_truth["target"], ground_truth["severity"],
              ground_truth["diagnosis_type"].replace("_", " ")]
    for val in checks:
        if val.lower() in response.lower():
            hits += 1
    return round(hits / len(checks), 2)

def consistency_score(responses: list) -> float:
    """
    Measures how consistent N responses are: fraction of response pairs
    that share at least 60% of their word tokens (Jaccard similarity).
    """
    if len(responses) < 2:
        return 1.0
    pairs = [(responses[i], responses[j])
             for i in range(len(responses)) for j in range(i+1, len(responses))]
    scores = []
    for a, b in pairs:
        wa, wb = extract_words(a.lower()), extract_words(b.lower())
        if not wa or not wb:
            scores.append(0.0)
            continue
        jaccard = len(wa & wb) / len(wa | wb)
        scores.append(jaccard)
    return round(sum(scores) / len(scores), 2)

def severity_match(response: str, ground_truth: dict) -> int:
    return 1 if ground_truth["severity"].lower() in response.lower() else 0

# ── Main ─────────────────────────────────────────────────────────────────────

SEP = "=" * 60

def run_condition(label: str, prompt: str, scenario: dict) -> dict:
    print(f"    [{label}] Running {N_RUNS} call(s)...", end=" ", flush=True)
    responses, times = [], []
    for _ in range(N_RUNS):
        text, ms = call_llm(prompt, MODEL_ABLATION)
        responses.append(text)
        times.append(ms)

    hall  = hallucination_rate(responses[0], scenario["known_entities"])
    conf  = conformity_score(responses[0], scenario["ground_truth"])
    cons  = consistency_score(responses)
    sev   = severity_match(responses[0], scenario["ground_truth"])
    avg_t = round(sum(times) / len(times), 0)

    print(f"done ({avg_t:.0f}ms avg)")
    print(f"         hallucination={hall:.2f}  conformity={conf:.2f}  consistency={cons:.2f}  severity_match={sev}")
    print(f"         Response: {responses[0][:120]}...")

    return {
        "condition":         label,
        "responses":         responses,
        "avg_time_ms":       avg_t,
        "hallucination_rate":hall,
        "conformity_score":  conf,
        "consistency_score": cons,
        "severity_match":    sev,
    }

def main():
    print(SEP)
    print("  ABLATION STUDY — PSC INF12")
    print(f"  Model: {MODEL_ABLATION}  |  Runs per condition: {N_RUNS}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEP)

    all_results = {
        "timestamp":  datetime.now().isoformat(),
        "model":      MODEL_ABLATION,
        "n_runs":     N_RUNS,
        "scenarios":  [],
    }

    for scenario in SCENARIOS:
        print(f"\n  Scenario: {scenario['id']}")
        print(f"  {scenario['description']}")
        print(f"  Ground truth: {scenario['ground_truth']}")

        results_A = run_condition("A - LLM alone",      build_prompt_A(scenario), scenario)
        results_B = run_condition("B - Level-1 -> LLM", build_prompt_B(scenario), scenario)
        results_C = run_condition("C - Level-1+2->LLM", build_prompt_C(scenario), scenario)

        all_results["scenarios"].append({
            "scenario_id":  scenario["id"],
            "description":  scenario["description"],
            "ground_truth": scenario["ground_truth"],
            "conditions":   [results_A, results_B, results_C],
        })

    # ── Summary table ────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  SUMMARY")
    print(SEP)
    header = f"  {'Scenario':<35} {'Cond':<20} {'Hall':>5} {'Conf':>5} {'Cons':>5} {'Sev':>4}"
    print(header)
    print("  " + "-" * 72)
    for sc in all_results["scenarios"]:
        for cond in sc["conditions"]:
            print(
                f"  {sc['scenario_id'][:35]:<35} {cond['condition'][:20]:<20} "
                f"{cond['hallucination_rate']:>5.2f} {cond['conformity_score']:>5.2f} "
                f"{cond['consistency_score']:>5.2f} {cond['severity_match']:>4}"
            )

    # ── Averages per condition ────────────────────────────────────────────────
    print(f"\n  {'Condition':<20} {'Avg Hall':>9} {'Avg Conf':>9} {'Avg Cons':>9} {'Avg Sev':>8}")
    print("  " + "-" * 58)
    for label in ["A - LLM alone", "B - Level-1 -> LLM", "C - Level-1+2->LLM"]:
        rows = [c for sc in all_results["scenarios"] for c in sc["conditions"] if c["condition"] == label]
        def avg(key): return round(sum(r[key] for r in rows) / len(rows), 2)
        print(f"  {label:<20} {avg('hallucination_rate'):>9.2f} {avg('conformity_score'):>9.2f} "
              f"{avg('consistency_score'):>9.2f} {avg('severity_match'):>8.2f}")

    print(SEP)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  Full results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
