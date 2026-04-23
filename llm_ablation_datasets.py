"""
llm_ablation_datasets.py

LLM 3-condition ablation on 9 synthetic datasets (aposteriori mode):
  A: LLM receives only the raw knowledge graph (Turtle)
  B: LLM receives graph + level-1 detector outputs
  C: LLM receives graph + level-1 + level-2 diagnoses

Evaluation: Precision@L2 / Recall@L2 / F1@L2 vs expected_level2.json
Same metrics as evaluate_datasets.py — direct comparison with MAS-only pipeline.

Usage:
    python -X utf8 llm_ablation_datasets.py              # 9 datasets
    python -X utf8 llm_ablation_datasets.py DS11 DS12    # specific
    python -X utf8 llm_ablation_datasets.py --gpu        # HuggingFace (GPU)

Output: llm_ablation_results.json
"""

from __future__ import annotations

import json, re, subprocess, sys, time, os
from pathlib import Path

import requests
from requests.auth import HTTPDigestAuth

# ── Config ──────────────────────────────────────────────────────────────────
PROJECT_ROOT  = Path(__file__).resolve().parent
DATASETS_DIR  = PROJECT_ROOT / "datasets"
RESULTS_DIR   = PROJECT_ROOT / "results"
PYTHON        = sys.executable

OLLAMA_URL    = "http://localhost:11434/api/generate"
OLLAMA_MODEL  = "llama3.1:8b"
HF_MODEL      = "mistralai/Mistral-7B-Instruct-v0.3"

CRUD_URL  = "http://localhost:8890/sparql-graph-crud-auth"
_AUTH     = HTTPDigestAuth("dba", "dba")
DS_GRAPH  = "http://dataset/"
NR_GRAPH  = "http://noria/"
ISQL      = Path("C:/Program Files/OpenLink Software/Virtuoso OpenSource 7.2/bin/isql.exe")
NORIA_DUMPS = Path("C:/Program Files/OpenLink Software/Virtuoso OpenSource 7.2/database/dumps")

TARGET_DATASETS = [
    "DS01_clean_baseA",
    "DS11_single_point_of_failure_basic",
    "DS12_change_induced_incident_basic",
    "DS13_service_cascade_basic",
    "DS14_traceability_breakdown_basic",
    "DS15_unstable_component_basic",
    "DS16_application_support_failure_basic",
    "DS17_local_infrastructure_cluster_basic",
    "DS23_three_diagnoses_ranked_by_urgency",
]

DIAGNOSERS_APOSTERIORI = [
    "single_point_of_failure_diagnoser",
    "change_induced_incident_diagnoser",
    "service_cascade_diagnoser",
    "traceability_breakdown_diagnoser",
    "unstable_component_diagnoser",
    "application_support_failure_diagnoser",
    "local_infrastructure_cluster_diagnoser",
]

DIAGNOSER_DESCRIPTIONS = {
    "single_point_of_failure_diagnoser":
        "A resource involved in an incident is isolated (low connectivity), has no redundant peer, and has high impact on dependent applications.",
    "change_induced_incident_diagnoser":
        "An infrastructure change was temporally followed by one or more incidents, and is linked to multiple incident records, suggesting it is the cause.",
    "service_cascade_diagnoser":
        "Multiple services or applications were simultaneously impacted by incidents sharing a common dependency (resource, module, or component).",
    "traceability_breakdown_diagnoser":
        "Incidents exist without associated trouble tickets, or trouble tickets exist without linked events, breaking the operational traceability chain.",
    "unstable_component_diagnoser":
        "A component has repeated events (burst or flapping), reopened or stale incidents, indicating chronic instability rather than a one-off failure.",
    "application_support_failure_diagnoser":
        "An application has an active incident but its support escalation chain is broken: missing procedure links, unresolved tickets, or absent resource coverage.",
    "local_infrastructure_cluster_diagnoser":
        "Multiple resources with simultaneous incidents share a location attribute or belong to the same local cluster, suggesting a local infrastructure event.",
}

# ── Backend detection ────────────────────────────────────────────────────────

def _ollama_available() -> bool:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

USE_HF = "--gpu" in sys.argv
USE_OLLAMA = not USE_HF and _ollama_available()

_hf_pipe = None

def _load_hf():
    global _hf_pipe
    if _hf_pipe is not None:
        return _hf_pipe
    from transformers import pipeline
    import torch
    print(f"  Loading {HF_MODEL} on GPU...", flush=True)
    _hf_pipe = pipeline(
        "text-generation", model=HF_MODEL,
        torch_dtype=torch.float16, device_map="auto",
    )
    return _hf_pipe

def call_llm(prompt: str) -> tuple[str, float]:
    t0 = time.perf_counter()
    if USE_HF:
        pipe = _load_hf()
        msgs = [{"role": "user", "content": prompt}]
        out = pipe(msgs, max_new_tokens=300, temperature=0.1, do_sample=True)
        text = out[0]["generated_text"][-1]["content"].strip()
    elif USE_OLLAMA:
        r = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300},
        }, timeout=300)
        text = r.json().get("response", "").strip()
    else:
        raise RuntimeError("No LLM backend available. Install Ollama or use --gpu.")
    elapsed = time.perf_counter() - t0
    return text, elapsed

# ── Virtuoso helpers ─────────────────────────────────────────────────────────

def _isql(sql: str, timeout: int = 60):
    return subprocess.run([str(ISQL), "localhost:1111", "dba", "dba"],
                         input=sql, capture_output=True, text=True, timeout=timeout)

def clear_virtuoso():
    _isql("DELETE FROM DB.DBA.RDF_QUAD WHERE "
          "id_to_iri(G) NOT LIKE 'http://www.openlinksw.com/%' "
          "AND id_to_iri(G) NOT LIKE 'http://www.w3.org/%';\n")

def load_ttl_http(path: Path, graph: str = DS_GRAPH, replace: bool = True):
    fn = requests.put if replace else requests.post
    r = fn(CRUD_URL, params={"graph": graph}, data=path.read_bytes(),
           headers={"Content-Type": "text/turtle"}, auth=_AUTH, timeout=60)
    if r.status_code not in (200, 201, 204):
        print(f"    WARN HTTP {r.status_code}: {r.text[:80]}")

def restore_noria():
    print("  Restoring noria-0.2...", end="", flush=True)
    clear_virtuoso()
    first = True
    for ttl in sorted(NORIA_DUMPS.glob("*.ttl")):
        load_ttl_http(ttl, NR_GRAPH, replace=first)
        first = False
    print(" done")

# ── MAS runner helpers ───────────────────────────────────────────────────────

def run_l1_agents(mode: str) -> dict[str, list]:
    """Run L1 agents for mode, return {agent_stem: [result_list]}."""
    agents_root = PROJECT_ROOT / "src" / "agt"
    agent_results = {}
    for path in sorted(agents_root.rglob("*.py")):
        if "__pycache__" in str(path) or "level2" in str(path):
            continue
        if mode in path.parts:
            subprocess.run([PYTHON, str(path)], capture_output=True, text=True,
                           cwd=PROJECT_ROOT,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=30)
    # Collect results written to results/
    for path in sorted(RESULTS_DIR.rglob("*.json")):
        if "level2" in str(path) or "campaign" in str(path) or "metrics" in str(path) or "baseline" in str(path):
            continue
        if f"/{mode}/" in str(path).replace("\\", "/"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    agent_results[path.stem] = data
            except Exception:
                pass
    return agent_results

def run_l2_agents(mode: str) -> dict[str, dict]:
    """Run L2 agents for mode, return {agent_stem: result_dict}."""
    agents_l2 = PROJECT_ROOT / "src" / "agt" / "level2" / mode
    results = {}
    for script in sorted(agents_l2.glob("*.py")):
        subprocess.run([PYTHON, str(script)], capture_output=True, text=True,
                       cwd=PROJECT_ROOT,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=30)
    for script in sorted(agents_l2.glob("*.py")):
        out = RESULTS_DIR / "level2" / mode / f"{script.stem}.json"
        if out.exists():
            results[script.stem] = json.loads(out.read_text(encoding="utf-8"))
    return results

# ── Summary builders ─────────────────────────────────────────────────────────

def _local_name(uri: str) -> str:
    """Extract local name from a URI."""
    local = uri.rstrip("/").split("/")[-1].split("#")[-1]
    if ":" in local:
        local = local.split(":")[-1]
    return local

def summarize_l1(agent_results: dict[str, list]) -> str:
    lines = ["Level-1 detector findings:"]
    found_any = False
    for agent, rows in sorted(agent_results.items()):
        if not rows:
            continue
        found_any = True
        entities = []
        for row in rows:
            for v in row.values():
                if isinstance(v, dict) and v.get("type") == "uri":
                    entities.append(_local_name(v["value"]))
        entities = list(dict.fromkeys(entities))[:6]
        lines.append(f"  - {agent}: {', '.join(entities)}")
    if not found_any:
        lines.append("  (no active detectors — all results empty)")
    return "\n".join(lines)

def summarize_l2(l2_results: dict[str, dict]) -> str:
    lines = ["Level-2 correlation diagnoses:"]
    found_any = False
    for agent, result in sorted(l2_results.items()):
        if result.get("activation_status") != "triggered":
            continue
        found_any = True
        diag = result.get("diagnoses", [{}])[0] if result.get("diagnoses") else {}
        anchor = diag.get("target_name") or diag.get("anchor", "?")
        rel = diag.get("reliability_score", "?")
        sev = diag.get("severity_score", "?")
        pri = diag.get("priority_score", "?")
        lines.append(f"  - {agent}: TRIGGERED  anchor={anchor}  reliability={rel}  severity={sev}  priority={pri}")
    if not found_any:
        lines.append("  (no diagnosers triggered)")
    return "\n".join(lines)

# ── Prompt builders ──────────────────────────────────────────────────────────

_DIAGNOSER_LIST = "\n".join(
    f"- {name}: {desc}"
    for name, desc in DIAGNOSER_DESCRIPTIONS.items()
)

_TASK = (
    "You are a network operations expert. Based on the information provided, "
    "determine which of the following diagnostic patterns apply to this infrastructure.\n\n"
    "Possible patterns:\n" + _DIAGNOSER_LIST + "\n\n"
    "Respond with ONLY a valid JSON object, no explanation:\n"
    '{"triggered": ["pattern_name1", ...], "primary_entities": {"pattern_name1": "entity", ...}}\n'
    "Use exact pattern names from the list. If nothing applies: "
    '{"triggered": [], "primary_entities": {}}'
)

def prompt_A(graph_ttl: str) -> str:
    return (
        _TASK + "\n\n"
        "--- KNOWLEDGE GRAPH (Turtle) ---\n" + graph_ttl
    )

def prompt_B(graph_ttl: str, l1_summary: str) -> str:
    return (
        _TASK + "\n\n"
        "--- KNOWLEDGE GRAPH (Turtle) ---\n" + graph_ttl + "\n\n"
        "--- " + l1_summary
    )

def prompt_C(graph_ttl: str, l1_summary: str, l2_summary: str) -> str:
    return (
        _TASK + "\n\n"
        "--- KNOWLEDGE GRAPH (Turtle) ---\n" + graph_ttl + "\n\n"
        "--- " + l1_summary + "\n\n"
        "--- " + l2_summary
    )

# ── LLM response parsing ─────────────────────────────────────────────────────

def parse_llm_response(text: str) -> list[str]:
    """Extract list of triggered diagnoser names from LLM JSON response."""
    # Try to find JSON block
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            d = json.loads(match.group())
            triggered = d.get("triggered", [])
            if isinstance(triggered, list):
                # Normalize: keep only known diagnoser names (fuzzy match)
                result = []
                for t in triggered:
                    t_clean = str(t).strip().lower().replace(" ", "_")
                    for d_name in DIAGNOSERS_APOSTERIORI:
                        if t_clean in d_name or d_name.replace("_diagnoser", "") in t_clean:
                            result.append(d_name)
                            break
                return list(dict.fromkeys(result))
        except json.JSONDecodeError:
            pass
    # Fallback: scan for known diagnoser names in text
    found = []
    text_lower = text.lower()
    for d_name in DIAGNOSERS_APOSTERIORI:
        base = d_name.replace("_diagnoser", "").replace("_", " ")
        if base in text_lower or d_name in text_lower:
            found.append(d_name)
    return found

# ── Evaluation ───────────────────────────────────────────────────────────────

def expected_triggered(ds_dir: Path, mode: str) -> list[str]:
    exp_path = ds_dir / "expected_level2.json"
    if not exp_path.exists():
        return []
    exp = json.loads(exp_path.read_text(encoding="utf-8-sig"))
    exp_mode = exp.get(mode, {})
    return [agent for agent, cases in exp_mode.items() if cases]

def compute_metrics(predicted: list[str], expected: list[str]) -> dict:
    pred_set = set(predicted)
    exp_set  = set(expected)
    tp = len(pred_set & exp_set)
    fp = len(pred_set - exp_set)
    fn = len(exp_set - pred_set)
    precision = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if not exp_set else 0.0)
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "precision": round(precision, 3),
        "recall":    round(recall, 3),
        "f1":        round(f1, 3),
        "tp": tp, "fp": fp, "fn": fn,
        "predicted": sorted(predicted),
        "expected":  sorted(expected),
    }

# ── Per-dataset evaluation ───────────────────────────────────────────────────

def evaluate_one(ds_dir: Path) -> dict:
    ds_id = ds_dir.name
    mode  = "aposteriori"
    print(f"\n  ── {ds_id}")

    # Load TTL into Virtuoso
    load_ttl_http(ds_dir / "dataset.ttl", DS_GRAPH, replace=True)
    graph_ttl = (ds_dir / "dataset.ttl").read_text(encoding="utf-8-sig")

    # Run L1 and L2 agents
    print("    Running L1...", end="", flush=True)
    t0 = time.perf_counter()
    l1_results = run_l1_agents(mode)
    print(f" {len([v for v in l1_results.values() if v])} active  {(time.perf_counter()-t0)*1000:.0f}ms", end="")
    print("  L2...", end="", flush=True)
    t1 = time.perf_counter()
    l2_results = run_l2_agents(mode)
    l2_triggered = [k for k, v in l2_results.items() if v.get("activation_status") == "triggered"]
    print(f" {len(l2_triggered)} triggered  {(time.perf_counter()-t1)*1000:.0f}ms")

    l1_summary = summarize_l1(l1_results)
    l2_summary = summarize_l2(l2_results)
    exp = expected_triggered(ds_dir, mode)

    condition_results = {}
    for cond_name, prompt in [
        ("A_graph_only",    prompt_A(graph_ttl)),
        ("B_graph_plus_L1", prompt_B(graph_ttl, l1_summary)),
        ("C_graph_L1_L2",   prompt_C(graph_ttl, l1_summary, l2_summary)),
    ]:
        print(f"    [{cond_name}] calling LLM...", end="", flush=True)
        t0 = time.perf_counter()
        response, _ = call_llm(prompt)
        elapsed = time.perf_counter() - t0
        predicted = parse_llm_response(response)
        metrics   = compute_metrics(predicted, exp)
        print(f" {elapsed:.1f}s  P={metrics['precision']:.2f} R={metrics['recall']:.2f} F1={metrics['f1']:.2f}  predicted={predicted}")
        condition_results[cond_name] = {
            "metrics": metrics,
            "elapsed_s": round(elapsed, 1),
            "raw_response": response[:400],
        }

    # MAS reference (from L2 run)
    mas_predicted = l2_triggered
    mas_metrics = compute_metrics(mas_predicted, exp)
    print(f"    [MAS_L1+L2_ref]        P={mas_metrics['precision']:.2f} R={mas_metrics['recall']:.2f} F1={mas_metrics['f1']:.2f}  triggered={mas_predicted}")

    return {
        "dataset_id": ds_id,
        "mode": mode,
        "expected": exp,
        "mas_reference": mas_metrics,
        "conditions": condition_results,
    }

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    model_label = HF_MODEL if USE_HF else (OLLAMA_MODEL if USE_OLLAMA else "none")

    print("=" * 64)
    print(f"  LLM ABLATION ON DATASETS  (model: {model_label})")
    print("=" * 64)

    # Select datasets
    datasets = []
    for d in sorted(DATASETS_DIR.iterdir()):
        if not d.is_dir() or not (d / "dataset.ttl").exists():
            continue
        if d.name not in TARGET_DATASETS:
            continue
        if args and not any(d.name.startswith(a) for a in args):
            continue
        datasets.append(d)

    print(f"  Running on {len(datasets)} datasets × 3 conditions = {len(datasets)*3} LLM calls")

    all_results = []
    for ds_dir in datasets:
        try:
            clear_virtuoso()
            r = evaluate_one(ds_dir)
            all_results.append(r)
        except Exception as e:
            print(f"  ERROR {ds_dir.name}: {e}")
            all_results.append({"dataset_id": ds_dir.name, "error": str(e)})

    restore_noria()

    # Summary
    print(f"\n{'='*64}")
    print("  SUMMARY — Precision / Recall / F1")
    print(f"{'='*64}")
    print(f"  {'Dataset':<45} {'Cond':>12} {'P':>6} {'R':>6} {'F1':>6}")
    print("  " + "─" * 74)

    agg = {"A_graph_only": [], "B_graph_plus_L1": [], "C_graph_L1_L2": [], "MAS": []}
    for r in all_results:
        if "error" in r:
            print(f"  {r['dataset_id']:<45}  ERROR")
            continue
        for cond, data in r["conditions"].items():
            m = data["metrics"]
            print(f"  {r['dataset_id']:<45} {cond:>12}  {m['precision']:>5.2f}  {m['recall']:>5.2f}  {m['f1']:>5.2f}")
            agg[cond].append(m)
        # MAS reference line
        m = r["mas_reference"]
        print(f"  {r['dataset_id']:<45} {'MAS_ref':>12}  {m['precision']:>5.2f}  {m['recall']:>5.2f}  {m['f1']:>5.2f}")
        agg["MAS"].append(m)

    print(f"\n  {'MACRO AVERAGES':<45}")
    print("  " + "─" * 74)
    for cond, metrics_list in agg.items():
        if not metrics_list:
            continue
        avg_p  = sum(m["precision"] for m in metrics_list) / len(metrics_list)
        avg_r  = sum(m["recall"]    for m in metrics_list) / len(metrics_list)
        avg_f1 = sum(m["f1"]        for m in metrics_list) / len(metrics_list)
        tp = sum(m["tp"] for m in metrics_list)
        fp = sum(m["fp"] for m in metrics_list)
        fn = sum(m["fn"] for m in metrics_list)
        print(f"  {cond:<45}  P={avg_p:.3f}  R={avg_r:.3f}  F1={avg_f1:.3f}  TP={tp} FP={fp} FN={fn}")

    out = PROJECT_ROOT / "llm_ablation_results.json"
    out.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Results saved to {out.name}")


if __name__ == "__main__":
    main()
