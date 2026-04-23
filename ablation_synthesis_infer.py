"""
ablation_synthesis_infer.py  —  GPU / INFERENCE phase (Experiment 3 redesigned)

Uses Mistral-7B-Instruct-v0.3 float16 on GPU (HuggingFace Transformers).
Reads llm_ablation_data.json (produced by prepare_llm_ablation.py).

For 5 representative ICT diagnostic scenarios, tests 3 conditions:
  A: LLM <- raw Turtle knowledge graph only
  B: LLM <- graph + Level-1 detector summaries
  C: LLM <- graph + Level-1 + Level-2 diagnosis summaries

Task: produce a free-form diagnostic report (root cause, entity, severity).
NOT pattern classification — the LLM must synthesise its own analysis
from the graph data, exactly as it would in a real operations context.

Metrics per (scenario, condition) over N_RUNS runs:
  - Conformite  : fraction of {anchor entity, severity, diagnosis keyword} found
  - Hallucination: fraction of NORIA-like names in response not present in graph
  - Severite    : binary — is the expected severity level mentioned?
  - Consistance : mean pairwise Jaccard similarity over N_RUNS runs

Writes ablation_synthesis_results.json.

Usage (on GPU server):
    python3 ablation_synthesis_infer.py
    python3 ablation_synthesis_infer.py --ollama   # force Ollama fallback
    python3 ablation_synthesis_infer.py --model <model_id>
"""

from __future__ import annotations

import json, re, sys, time
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

HF_MODEL_DEFAULT = "mistralai/Mistral-7B-Instruct-v0.3"
OLLAMA_URL       = "http://localhost:11434/api/generate"
OLLAMA_MODEL     = "llama3.1:8b"
DATA_FILE        = Path("llm_ablation_data.json")
OUT_FILE         = Path("ablation_synthesis_results.json")
N_RUNS           = 3   # runs per (scenario, condition) — temperature=0.1 so runs ~stable

# ── Scenario definitions ──────────────────────────────────────────────────────
# Ground truth derived from L2 diagnoser results on each dataset.
# anchor: the primary affected entity (local name, case-insensitive match).
# expected_severity: the severity level we expect the LLM to identify.
# diagnosis_keywords: synonyms / key phrases for the diagnostic pattern.

SCENARIOS = [
    {
        "id": "S1_SPOF",
        "label": "Single Point of Failure (aposteriori)",
        "dataset_id": "DS11_single_point_of_failure_basic",
        "mode": "aposteriori",
        "anchor": "res_firewall_01",
        "expected_severity": "CRITICAL",
        "diagnosis_keywords": [
            "single point", "spof", "no redundan", "isolated", "unavailable", "sole"
        ],
    },
    {
        "id": "S2_Change",
        "label": "Change-induced incident (aposteriori)",
        "dataset_id": "DS12_change_induced_incident_basic",
        "mode": "aposteriori",
        "anchor": "change_customer_release",
        "expected_severity": "HIGH",
        "diagnosis_keywords": [
            "change", "induced", "caused", "following", "deployment", "release", "update"
        ],
    },
    {
        "id": "S3_Traceability",
        "label": "Traceability breakdown (aposteriori)",
        "dataset_id": "DS14_traceability_breakdown_basic",
        "mode": "aposteriori",
        "anchor": "operational_process",
        "expected_severity": "HIGH",
        "diagnosis_keywords": [
            "traceability", "unlinked", "no ticket", "without ticket",
            "missing link", "not linked", "orphan", "no associated"
        ],
    },
    {
        "id": "S4_Fragility",
        "label": "Structural fragility (apriori)",
        "dataset_id": "DS04_structural_fragility_resource_anchor",
        "mode": "apriori",
        "anchor": "res_access_switch_02",
        "expected_severity": "HIGH",
        "diagnosis_keywords": [
            "structural", "fragil", "weakness", "multiple weak", "missing interface",
            "no redundan", "no support", "architectural"
        ],
    },
    {
        "id": "S5_Cascade",
        "label": "Service cascade / mixed (aposteriori)",
        "dataset_id": "DS18_aposteriori_mixed_two_true_diagnoses",
        "mode": "aposteriori",
        "anchor": "service_workforce_portal",
        "expected_severity": "CRITICAL",
        "diagnosis_keywords": [
            "cascade", "multiple service", "propagat", "simultaneous",
            "shared dependency", "common resource", "several"
        ],
    },
]

# ── Backend ───────────────────────────────────────────────────────────────────

_args = sys.argv[1:]
FORCE_OLLAMA = "--ollama" in _args
HF_MODEL = HF_MODEL_DEFAULT
for i, a in enumerate(_args):
    if a == "--model" and i + 1 < len(_args):
        HF_MODEL = _args[i + 1]

_hf_pipe = None


def _load_hf():
    global _hf_pipe
    if _hf_pipe is not None:
        return _hf_pipe
    from transformers import pipeline
    import torch
    print(f"  Loading {HF_MODEL}...", flush=True)
    _hf_pipe = pipeline(
        "text-generation", model=HF_MODEL,
        torch_dtype=torch.float16, device_map="auto",
    )
    print("  Model loaded.", flush=True)
    return _hf_pipe


def call_llm(prompt: str) -> tuple[str, float]:
    t0 = time.perf_counter()
    if not FORCE_OLLAMA:
        pipe = _load_hf()
        msgs = [{"role": "user", "content": prompt}]
        out = pipe(msgs, max_new_tokens=300, temperature=0.1, do_sample=True)
        text = out[0]["generated_text"][-1]["content"].strip()
    else:
        import requests
        r = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300},
        }, timeout=300)
        text = r.json().get("response", "").strip()
    return text, time.perf_counter() - t0

# ── Prompt builders ───────────────────────────────────────────────────────────

SYNTHESIS_TASK = (
    "You are a network operations expert analyzing an ICT infrastructure knowledge graph.\n"
    "Based on the data provided, produce a concise diagnostic report:\n"
    "  - Identify the most likely root cause of the main operational issue\n"
    "  - Name the primary affected entity (use the exact identifier from the graph)\n"
    "  - Assess the severity: CRITICAL, HIGH, MEDIUM, or LOW\n"
    "Answer in 3 to 5 sentences. Do not classify patterns by name — "
    "synthesise a natural language diagnosis from the evidence."
)


def prompt_A(graph_ttl: str) -> str:
    return SYNTHESIS_TASK + "\n\n--- KNOWLEDGE GRAPH (Turtle) ---\n" + graph_ttl


def prompt_B(graph_ttl: str, l1: str) -> str:
    return SYNTHESIS_TASK + "\n\n--- KNOWLEDGE GRAPH (Turtle) ---\n" + graph_ttl + "\n\n--- " + l1


def prompt_C(graph_ttl: str, l1: str, l2: str) -> str:
    return (SYNTHESIS_TASK + "\n\n--- KNOWLEDGE GRAPH (Turtle) ---\n" + graph_ttl
            + "\n\n--- " + l1 + "\n\n--- " + l2)

# ── Metrics ───────────────────────────────────────────────────────────────────

_GENERIC_TOKENS = {
    "CRITICAL", "HIGH", "MEDIUM", "LOW", "ICT", "LLM", "MAS", "JSON", "TTL",
    "RDF", "SPARQL", "NOTE", "NORIA", "KB", "DC", "SLA", "ITSM", "API",
    "URL", "ID", "OK", "NA", "KPI", "TP", "FP", "FN",
}


def _graph_entities(ttl: str) -> set[str]:
    """All local names in the Turtle graph (lowercase for matching)."""
    names = re.findall(r'[\s(,;](\w[\w\d_-]{2,})\b', ttl)
    return {n.lower() for n in names if not n.startswith("http")}


def _response_named_entities(text: str) -> list[str]:
    """NORIA-like entity tokens from LLM response (uppercase with underscores/digits)."""
    tokens = re.findall(r'\b([A-Z][A-Z_0-9]{2,})\b', text)
    return [t for t in tokens if t not in _GENERIC_TOKENS]


def compute_conformite(response: str, scenario: dict) -> float:
    """
    Score in {0, 1/3, 2/3, 1}: fraction of 3 ground truth elements found.
    1. Anchor entity (case-insensitive substring)
    2. Expected severity keyword
    3. Any diagnosis keyword (case-insensitive)
    """
    rl = response.lower()
    hits = 0
    if scenario["anchor"].lower() in rl:
        hits += 1
    if scenario["expected_severity"].lower() in rl:
        hits += 1
    if any(kw in rl for kw in scenario["diagnosis_keywords"]):
        hits += 1
    return round(hits / 3, 3)


def compute_hallucination(response: str, graph_ents: set[str]) -> float:
    """Fraction of NORIA-like tokens in response not present in the graph."""
    tokens = _response_named_entities(response)
    if not tokens:
        return 0.0
    unknown = [t for t in tokens if t.lower() not in graph_ents]
    return round(len(unknown) / len(tokens), 3)


def compute_severite(response: str, expected: str) -> int:
    return 1 if expected.lower() in response.lower() else 0


def compute_consistance(responses: list[str]) -> float:
    if len(responses) < 2:
        return 1.0
    def jaccard(a: str, b: str) -> float:
        ta, tb = set(a.lower().split()), set(b.lower().split())
        if not ta or not tb:
            return 0.0
        return len(ta & tb) / len(ta | tb)
    pairs = [(i, j) for i in range(len(responses)) for j in range(i + 1, len(responses))]
    return round(sum(jaccard(responses[i], responses[j]) for i, j in pairs) / len(pairs), 3)

# ── Aggregation ───────────────────────────────────────────────────────────────

def macro_avg(rows: list[dict]) -> dict:
    if not rows:
        return {}
    n = len(rows)
    return {
        "conformite":    round(sum(r["conformite"]    for r in rows) / n, 3),
        "hallucination": round(sum(r["hallucination"] for r in rows) / n, 3),
        "severite":      round(sum(r["severite"]      for r in rows) / n, 3),
        "consistance":   round(sum(r["consistance"]   for r in rows) / n, 3),
        "n": n,
    }

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found. Run prepare_llm_ablation.py first.")
        sys.exit(1)

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    lookup = {(e["dataset_id"], e["mode"]): e for e in data}
    model_label = HF_MODEL if not FORCE_OLLAMA else OLLAMA_MODEL

    n_calls = len(SCENARIOS) * 3 * N_RUNS
    print("=" * 68)
    print(f"  LLM SYNTHESIS ABLATION  model={model_label}")
    print(f"  {len(SCENARIOS)} scenarios × 3 conditions × {N_RUNS} runs = {n_calls} LLM calls")
    print(f"  Task: free-form diagnostic report  (NOT pattern classification)")
    print("=" * 68)

    all_results = []
    CONDITIONS = [
        ("A_graph_only",    lambda e: prompt_A(e["graph_ttl"])),
        ("B_graph_plus_L1", lambda e: prompt_B(e["graph_ttl"], e["l1_summary"])),
        ("C_graph_L1_L2",   lambda e: prompt_C(e["graph_ttl"], e["l1_summary"], e["l2_summary"])),
    ]

    for sc in SCENARIOS:
        key = (sc["dataset_id"], sc["mode"])
        if key not in lookup:
            print(f"  WARN: {key} not found in data — skipping")
            continue
        entry = lookup[key]
        graph_ents = _graph_entities(entry["graph_ttl"])

        print(f"\n  ── {sc['id']} : {sc['label']}")
        print(f"     anchor={sc['anchor']}  expected_severity={sc['expected_severity']}")

        sc_result = {
            "scenario": sc["id"], "label": sc["label"],
            "dataset_id": sc["dataset_id"], "mode": sc["mode"],
            "anchor": sc["anchor"], "expected_severity": sc["expected_severity"],
            "model": model_label, "conditions": {},
        }

        for cond_name, prompt_fn in CONDITIONS:
            prompt = prompt_fn(entry)
            print(f"    [{cond_name}] {N_RUNS} runs...", end="", flush=True)
            responses = []
            t_total = 0.0
            for _ in range(N_RUNS):
                resp, t = call_llm(prompt)
                responses.append(resp)
                t_total += t

            conf  = [compute_conformite(r, sc) for r in responses]
            hall  = [compute_hallucination(r, graph_ents) for r in responses]
            sev   = [compute_severite(r, sc["expected_severity"]) for r in responses]
            cons  = compute_consistance(responses)

            avg_conf = round(sum(conf) / len(conf), 3)
            avg_hall = round(sum(hall) / len(hall), 3)
            avg_sev  = round(sum(sev)  / len(sev),  3)

            print(f" Conf={avg_conf:.2f}  Hall={avg_hall:.2f}  "
                  f"Sev={avg_sev:.2f}  Cons={cons:.2f}  ({t_total:.1f}s)")

            sc_result["conditions"][cond_name] = {
                "conformite":    avg_conf,
                "hallucination": avg_hall,
                "severite":      avg_sev,
                "consistance":   cons,
                "elapsed_s":     round(t_total, 1),
                "responses":     [r[:400] for r in responses],
            }

        all_results.append(sc_result)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*68}")
    print(f"  MACRO AVERAGES  ({len(all_results)} scenarios)")
    print(f"{'='*68}")

    summary = {}
    for cond_name, _ in CONDITIONS:
        rows = [r["conditions"][cond_name] for r in all_results
                if cond_name in r["conditions"]]
        agg = macro_avg(rows)
        summary[cond_name] = agg
        print(f"  {cond_name:<25} "
              f"Conf={agg['conformite']:.3f}  Hall={agg['hallucination']:.3f}  "
              f"Sev={agg['severite']:.3f}  Cons={agg['consistance']:.3f}")

    OUT_FILE.write_text(json.dumps({
        "model": model_label,
        "n_runs": N_RUNS,
        "task": "synthesis",
        "results": all_results,
        "macro_averages": summary,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Results saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
