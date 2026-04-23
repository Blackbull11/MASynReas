"""
llm_ablation_infer.py  —  GPU / INFERENCE phase

Reads llm_ablation_data.json (produced by prepare_llm_ablation.py)
and runs 3 LLM conditions per (dataset, mode) pair:
  A: LLM ← raw knowledge graph (Turtle)
  B: LLM ← graph + level-1 detector outputs
  C: LLM ← graph + level-1 + level-2 diagnoses

Supports both apriori and aposteriori modes. The diagnoser list and
descriptions in the prompt are selected based on each entry's mode field.

Writes llm_ablation_results.json with Precision@L2 / Recall@L2 / F1@L2
per condition — directly comparable to the MAS evaluation results.

Usage (on GPU server):
    python3 llm_ablation_infer.py                         # auto HuggingFace
    python3 llm_ablation_infer.py --ollama                # force Ollama
    python3 llm_ablation_infer.py --model <model_id>      # custom HF model
"""

from __future__ import annotations

import json, re, sys, time
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────

HF_MODEL_DEFAULT = "mistralai/Mistral-7B-Instruct-v0.3"
OLLAMA_URL       = "http://localhost:11434/api/generate"
OLLAMA_MODEL     = "llama3.1:8b"
DATA_FILE        = Path("llm_ablation_data.json")
OUT_FILE         = Path("llm_ablation_results.json")

DIAGNOSERS_APOSTERIORI = [
    "single_point_of_failure_diagnoser",
    "change_induced_incident_diagnoser",
    "service_cascade_diagnoser",
    "traceability_breakdown_diagnoser",
    "unstable_component_diagnoser",
    "application_support_failure_diagnoser",
    "local_infrastructure_cluster_diagnoser",
]

DIAGNOSERS_APRIORI = [
    "structural_fragility_diagnoser",
    "critical_service_exposure_diagnoser",
    "observability_gap_diagnoser",
    "procedural_unreadiness_diagnoser",
    "functional_mapping_gap_diagnoser",
]

DIAGNOSER_DESCRIPTIONS = {
    # aposteriori
    "single_point_of_failure_diagnoser":
        "A resource involved in an incident is isolated (weak connectivity), has no redundant peer, and has high impact on dependent applications.",
    "change_induced_incident_diagnoser":
        "An infrastructure change was temporally followed by one or more incidents, and is linked to multiple incident records.",
    "service_cascade_diagnoser":
        "Multiple services or applications were simultaneously impacted by incidents sharing a common dependency.",
    "traceability_breakdown_diagnoser":
        "Incidents without associated trouble tickets, or trouble tickets without linked events, breaking the operational traceability chain.",
    "unstable_component_diagnoser":
        "A component has repeated events (burst or flapping), reopened or stale incidents, indicating chronic instability.",
    "application_support_failure_diagnoser":
        "An application has an active incident but its support escalation chain is broken: missing procedure links or absent resource coverage.",
    "local_infrastructure_cluster_diagnoser":
        "Multiple resources with simultaneous incidents share a location attribute or belong to the same local cluster.",
    # apriori
    "structural_fragility_diagnoser":
        "A resource or application exhibits multiple structural weaknesses (missing interface, missing redundancy, no support application) simultaneously, indicating architectural fragility.",
    "critical_service_exposure_diagnoser":
        "A critical service is exposed: its supporting resources lack redundancy, or the service has excessive dependency concentration on a single resource or application.",
    "observability_gap_diagnoser":
        "Events or changes exist without proper linkage to observable elements, or monitoring coverage is missing for key resources, creating blind spots.",
    "procedural_unreadiness_diagnoser":
        "Trouble tickets exist without assigned resolution procedures, or change requests are missing scheduled execution times, indicating operational unpreparedness.",
    "functional_mapping_gap_diagnoser":
        "Applications exist without supporting resources or modules, or services exist without application coverage, indicating incomplete functional mapping.",
}

# ── Backend ──────────────────────────────────────────────────────────────────

_args = sys.argv[1:]
FORCE_OLLAMA = "--ollama" in _args
HF_MODEL = HF_MODEL_DEFAULT
for i, a in enumerate(_args):
    if a == "--model" and i + 1 < len(_args):
        HF_MODEL = _args[i + 1]

_hf_pipe = None


def _ollama_available():
    try:
        import requests
        return requests.get("http://localhost:11434/api/tags", timeout=3).status_code == 200
    except Exception:
        return False


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

def _build_task(diagnosers: list[str]) -> str:
    desc_list = "\n".join(f"- {n}: {DIAGNOSER_DESCRIPTIONS[n]}" for n in diagnosers)
    return (
        "You are a network operations expert analyzing an ICT infrastructure knowledge graph.\n"
        "Determine which of the following diagnostic patterns apply based on the data provided.\n\n"
        "Patterns:\n" + desc_list + "\n\n"
        "Respond with ONLY valid JSON (no explanation, no markdown):\n"
        '{"triggered": ["pattern_name1", ...], "primary_entities": {"pattern_name1": "entity"}}\n'
        "Use exact pattern names. If nothing applies: "
        '{"triggered": [], "primary_entities": {}}'
    )


def prompt_A(graph_ttl: str, task: str) -> str:
    return task + "\n\n--- KNOWLEDGE GRAPH (Turtle) ---\n" + graph_ttl


def prompt_B(graph_ttl: str, l1: str, task: str) -> str:
    return task + "\n\n--- KNOWLEDGE GRAPH (Turtle) ---\n" + graph_ttl + "\n\n--- " + l1


def prompt_C(graph_ttl: str, l1: str, l2: str, task: str) -> str:
    return task + "\n\n--- KNOWLEDGE GRAPH (Turtle) ---\n" + graph_ttl + "\n\n--- " + l1 + "\n\n--- " + l2

# ── Parsing & metrics ────────────────────────────────────────────────────────

def parse_response(text: str, diagnosers: list[str]) -> list[str]:
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try:
            d = json.loads(m.group())
            triggered = d.get("triggered", [])
            result = []
            for t in triggered:
                t_norm = str(t).strip().lower().replace(" ", "_").replace("-", "_")
                for name in diagnosers:
                    base = name.replace("_diagnoser", "")
                    if t_norm == name or base in t_norm or t_norm in base:
                        result.append(name)
                        break
            return list(dict.fromkeys(result))
        except json.JSONDecodeError:
            pass
    found = []
    tl = text.lower()
    for name in diagnosers:
        base = name.replace("_diagnoser", "").replace("_", " ")
        if name in tl or base in tl:
            found.append(name)
    return found


def metrics(predicted: list[str], expected: list[str]) -> dict:
    p, e = set(predicted), set(expected)
    tp = len(p & e)
    fp = len(p - e)
    fn = len(e - p)
    prec = tp / (tp + fp) if (tp + fp) else (1.0 if not e else 0.0)
    rec  = tp / (tp + fn) if (tp + fn) else 1.0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3),
            "tp": tp, "fp": fp, "fn": fn, "predicted": sorted(predicted), "expected": sorted(expected)}

# ── Aggregation helpers ───────────────────────────────────────────────────────

def macro_avg(ms: list[dict]) -> dict:
    if not ms:
        return {}
    n = len(ms)
    return {
        "precision": round(sum(m["precision"] for m in ms) / n, 3),
        "recall":    round(sum(m["recall"]    for m in ms) / n, 3),
        "f1":        round(sum(m["f1"]        for m in ms) / n, 3),
        "tp": sum(m["tp"] for m in ms),
        "fp": sum(m["fp"] for m in ms),
        "fn": sum(m["fn"] for m in ms),
        "n":  n,
    }

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found. Run prepare_llm_ablation.py first.")
        sys.exit(1)

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    model_label = HF_MODEL if not FORCE_OLLAMA else OLLAMA_MODEL

    n_apriori    = sum(1 for e in data if e["mode"] == "apriori")
    n_aposteriori = sum(1 for e in data if e["mode"] == "aposteriori")

    print("=" * 64)
    print(f"  LLM ABLATION INFERENCE  model={model_label}")
    print(f"  {len(data)} (dataset,mode) pairs × 3 conditions = {len(data)*3} calls")
    print(f"  apriori={n_apriori}  aposteriori={n_aposteriori}")
    print("=" * 64)

    all_results = []

    for entry in data:
        ds_id    = entry["dataset_id"]
        mode     = entry["mode"]
        expected = entry["expected"]
        mas_ref  = entry["mas_triggered"]

        diagnosers = DIAGNOSERS_APRIORI if mode == "apriori" else DIAGNOSERS_APOSTERIORI
        task       = _build_task(diagnosers)

        graph_ttl  = entry["graph_ttl"]
        l1_summary = entry["l1_summary"]
        l2_summary = entry["l2_summary"]

        print(f"\n  ── {ds_id} [{mode}]  (expected: {expected})")

        conditions = {}
        for cond_name, prompt in [
            ("A_graph_only",    prompt_A(graph_ttl, task)),
            ("B_graph_plus_L1", prompt_B(graph_ttl, l1_summary, task)),
            ("C_graph_L1_L2",   prompt_C(graph_ttl, l1_summary, l2_summary, task)),
        ]:
            print(f"    [{cond_name}]...", end="", flush=True)
            response, elapsed = call_llm(prompt)
            predicted = parse_response(response, diagnosers)
            m = metrics(predicted, expected)
            print(f" {elapsed:.1f}s  predicted={predicted}  P={m['precision']:.2f} R={m['recall']:.2f} F1={m['f1']:.2f}")
            conditions[cond_name] = {
                "metrics": m, "elapsed_s": round(elapsed, 1),
                "raw_response": response[:500],
            }

        mas_metrics = metrics(mas_ref, expected)
        print(f"    [MAS_reference]       triggered={mas_ref}  P={mas_metrics['precision']:.2f} R={mas_metrics['recall']:.2f} F1={mas_metrics['f1']:.2f}")

        all_results.append({
            "dataset_id": ds_id,
            "mode": mode,
            "model": model_label,
            "expected": expected,
            "mas_reference": mas_metrics,
            "conditions": conditions,
        })

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*64}")
    print("  MACRO AVERAGES")
    print(f"{'='*64}")

    CONDITIONS = ["A_graph_only", "B_graph_plus_L1", "C_graph_L1_L2"]

    def summarize(subset: list[dict], label: str):
        if not subset:
            return []
        print(f"\n  {label} ({len(subset)} pairs):")
        rows = []
        for cond in CONDITIONS:
            ms = [r["conditions"][cond]["metrics"] for r in subset]
            agg = macro_avg(ms)
            print(f"    {cond:<25} P={agg['precision']:.3f}  R={agg['recall']:.3f}  F1={agg['f1']:.3f}  TP={agg['tp']} FP={agg['fp']} FN={agg['fn']}")
            rows.append({"condition": cond, **agg})
        mas_ms = [r["mas_reference"] for r in subset]
        agg_mas = macro_avg(mas_ms)
        print(f"    {'MAS_reference':<25} P={agg_mas['precision']:.3f}  R={agg_mas['recall']:.3f}  F1={agg_mas['f1']:.3f}  TP={agg_mas['tp']} FP={agg_mas['fp']} FN={agg_mas['fn']}")
        rows.append({"condition": "MAS_reference", **agg_mas})
        return rows

    all_rows   = summarize(all_results, "ALL (36 pairs)")
    apri_rows  = summarize([r for r in all_results if r["mode"] == "apriori"],  "APRIORI")
    apost_rows = summarize([r for r in all_results if r["mode"] == "aposteriori"], "APOSTERIORI")

    OUT_FILE.write_text(json.dumps({
        "model": model_label,
        "results": all_results,
        "macro_averages": {
            "all":         all_rows,
            "apriori":     apri_rows,
            "aposteriori": apost_rows,
        },
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Results saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
