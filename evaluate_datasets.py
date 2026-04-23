"""
evaluate_datasets.py

Evaluates the full MAS pipeline (level-1 + level-2) against the synthetic
dataset catalogue (datasets/DS*). For each dataset:
  1. Loads dataset.ttl into Virtuoso (replaces current graph)
  2. Runs all relevant level-1 detectors
  3. Runs all level-2 diagnosers for the dataset's mode
  4. Compares outputs against expected_level1.json and expected_level2.json
  5. Reports Precision@L2, Recall@L2, false positive rate, activation correctness

Restores noria-0.2 at the end.

Usage:
    python -X utf8 evaluate_datasets.py               # all datasets
    python -X utf8 evaluate_datasets.py DS01 DS11     # specific datasets
    python -X utf8 evaluate_datasets.py --apriori     # apriori datasets only
    python -X utf8 evaluate_datasets.py --aposteriori # aposteriori datasets only

Output:
    eval_results.json
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import requests
from requests.auth import HTTPDigestAuth

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).resolve().parent
DATASETS_DIR  = PROJECT_ROOT / "datasets"
RESULTS_DIR   = PROJECT_ROOT / "results"
ISQL          = Path("C:/Program Files/OpenLink Software/Virtuoso OpenSource 7.2/bin/isql.exe")
NORIA_DUMPS   = Path("C:/Program Files/OpenLink Software/Virtuoso OpenSource 7.2/database/dumps")
PYTHON        = sys.executable

LEVEL2_APRIORI = [
    "structural_fragility_diagnoser",
    "critical_service_exposure_diagnoser",
    "observability_gap_diagnoser",
    "procedural_unreadiness_diagnoser",
    "functional_mapping_gap_diagnoser",
]
LEVEL2_APOSTERIORI = [
    "single_point_of_failure_diagnoser",
    "change_induced_incident_diagnoser",
    "service_cascade_diagnoser",
    "traceability_breakdown_diagnoser",
    "unstable_component_diagnoser",
    "application_support_failure_diagnoser",
    "local_infrastructure_cluster_diagnoser",
]

# Reliability/severity numeric → qualitative label (matches expected_level2.json)
def _rel_label(score: int) -> str:
    if score >= 80: return "very_high"
    if score >= 60: return "high"
    if score >= 40: return "plausible"
    return "weak"

def _sev_label(score: int) -> str:
    if score >= 75: return "critical"
    if score >= 50: return "high"
    if score >= 25: return "moderate"
    return "low"

# ─────────────────────────────────────────────────────────────────────────────
# VIRTUOSO HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _isql(sql: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(ISQL), "localhost:1111", "dba", "dba"],
        input=sql, capture_output=True, text=True, timeout=timeout,
    )

_CRUD_URL = "http://localhost:8890/sparql-graph-crud-auth"
_AUTH     = HTTPDigestAuth("dba", "dba")
_DS_GRAPH = "http://dataset/"
_NR_GRAPH = "http://noria/"

def clear_virtuoso():
    _isql(
        "DELETE FROM DB.DBA.RDF_QUAD WHERE "
        "id_to_iri(G) NOT LIKE 'http://www.openlinksw.com/%' "
        "AND id_to_iri(G) NOT LIKE 'http://www.w3.org/%';\n"
    )

def _http_load_ttl(ttl_path: Path, graph: str, replace: bool = True) -> None:
    content = ttl_path.read_bytes()
    fn = requests.put if replace else requests.post
    r = fn(_CRUD_URL, params={"graph": graph}, data=content,
           headers={"Content-Type": "text/turtle"}, auth=_AUTH, timeout=60)
    if r.status_code not in (200, 201, 204):
        print(f"    WARN HTTP load {r.status_code}: {r.text[:120]}")

def load_ttl(ttl_path: Path):
    _http_load_ttl(ttl_path, _DS_GRAPH, replace=True)

def restore_noria():
    print("  Restoring noria-0.2...", end="", flush=True)
    clear_virtuoso()
    first = True
    for ttl in sorted(NORIA_DUMPS.glob("*.ttl")):
        _http_load_ttl(ttl, _NR_GRAPH, replace=first)
        first = False
    print(f" {triple_count()} triples")

def triple_count() -> int:
    # Count only user triples (exclude Virtuoso system graphs)
    r = _isql(
        "SELECT COUNT(*) FROM DB.DBA.RDF_QUAD WHERE "
        "id_to_iri(G) NOT LIKE 'http://www.openlinksw.com/%' "
        "AND id_to_iri(G) NOT LIKE 'http://www.w3.org/%';\n"
    )
    for l in r.stdout.splitlines():
        if l.strip().isdigit():
            return int(l.strip())
    return -1

# ─────────────────────────────────────────────────────────────────────────────
# AGENT RUNNERS
# ─────────────────────────────────────────────────────────────────────────────

def run_level1(mode: str) -> dict:
    """Run all level-1 detectors for mode, return {script: ok/fail}."""
    results = {}
    agents_root = PROJECT_ROOT / "src" / "agt"
    for path in sorted(agents_root.rglob("*.py")):
        if "__pycache__" in str(path) or "level2" in str(path):
            continue
        if mode in path.parts:
            r = subprocess.run(
                [PYTHON, str(path)], capture_output=True, text=True,
                cwd=PROJECT_ROOT,
                env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
                timeout=30,
            )
            results[path.stem] = r.returncode == 0
    return results

def run_level2(mode: str) -> dict:
    """Run all level-2 diagnosers for mode, return {agent: result_dict}."""
    agents = LEVEL2_APRIORI if mode == "apriori" else LEVEL2_APOSTERIORI
    results = {}
    for agent in agents:
        script = PROJECT_ROOT / "src" / "agt" / "level2" / mode / f"{agent}.py"
        if not script.exists():
            continue
        r = subprocess.run(
            [PYTHON, str(script)], capture_output=True, text=True,
            cwd=PROJECT_ROOT,
            env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
            timeout=30,
        )
        out_path = RESULTS_DIR / "level2" / mode / f"{agent}.json"
        if out_path.exists():
            results[agent] = json.loads(out_path.read_text(encoding="utf-8"))
        else:
            results[agent] = {"activation_status": "error", "diagnoses": []}
    return results

# ─────────────────────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_l2_metrics(actual: dict, expected_l2: dict, mode: str) -> dict:
    exp_mode = expected_l2.get(mode, {})

    tp = fp = fn = 0
    detail = {}

    for agent, act_result in actual.items():
        triggered = act_result.get("activation_status") == "triggered"
        exp_diagnoses = exp_mode.get(agent, [])
        expected_triggered = len(exp_diagnoses) > 0

        if triggered and expected_triggered:
            tp += 1
            detail[agent] = "TP"
        elif triggered and not expected_triggered:
            fp += 1
            detail[agent] = "FP"
        elif not triggered and expected_triggered:
            fn += 1
            detail[agent] = "FN"
        else:
            detail[agent] = "TN"

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision_at_l2": round(precision, 3),
        "recall_at_l2":    round(recall, 3),
        "f1_at_l2":        round(f1, 3),
        "tp": tp, "fp": fp, "fn": fn,
        "detail": detail,
    }

def compute_l1_metrics(actual_l1: dict, expected_l1: dict, mode: str) -> dict:
    """Check which expected non-zero agents actually fired."""
    exp_mode = expected_l1.get(mode, {})
    expected_nonzero = set()
    for family, agents in exp_mode.items():
        for agent, results in agents.items():
            if results:  # non-empty list = expected to fire
                expected_nonzero.add(agent)

    actual_nonzero = {agent for agent, ok in actual_l1.items() if ok}
    hit = expected_nonzero & actual_nonzero
    missed = expected_nonzero - actual_nonzero

    recall = len(hit) / len(expected_nonzero) if expected_nonzero else 1.0
    return {
        "expected_nonzero": sorted(expected_nonzero),
        "hit": sorted(hit),
        "missed": sorted(missed),
        "recall_at_l1": round(recall, 3),
    }

# ─────────────────────────────────────────────────────────────────────────────
# PER-DATASET EVALUATION
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_dataset(ds_dir: Path) -> dict:
    manifest_path = ds_dir / "manifest.json"
    if not manifest_path.exists():
        return {"error": "no manifest"}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    ds_id    = manifest["dataset_id"]
    mode_raw = manifest.get("mode", "both")
    modes    = ["apriori", "aposteriori"] if mode_raw == "both" else [mode_raw]

    expected_l1 = json.loads((ds_dir / "expected_level1.json").read_text(encoding="utf-8-sig")) if (ds_dir / "expected_level1.json").exists() else {}
    expected_l2 = json.loads((ds_dir / "expected_level2.json").read_text(encoding="utf-8-sig")) if (ds_dir / "expected_level2.json").exists() else {}

    print(f"\n  {'─'*56}")
    print(f"  {ds_id}  [{mode_raw}]")

    # Load dataset into Virtuoso
    print(f"  Loading TTL...", end="", flush=True)
    clear_virtuoso()
    load_ttl(ds_dir / "dataset.ttl")
    n = triple_count()
    print(f" {n} triples")

    result = {"dataset_id": ds_id, "mode": mode_raw, "triples": n, "modes": {}}

    for mode in modes:
        print(f"  [{mode}] running level-1...", end="", flush=True)
        t0 = time.perf_counter()
        l1_status = run_level1(mode)
        t1 = time.perf_counter()
        print(f" {len(l1_status)} agents  {(t1-t0)*1000:.0f}ms", end="")

        print(f"  → level-2...", end="", flush=True)
        l2_results = run_level2(mode)
        t2 = time.perf_counter()
        print(f" {len(l2_results)} agents  {(t2-t1)*1000:.0f}ms")

        l1_metrics = compute_l1_metrics(l1_status, expected_l1, mode)
        l2_metrics = compute_l2_metrics(l2_results, expected_l2, mode)

        # Print triggered agents
        triggered = [a for a, r in l2_results.items() if r.get("activation_status") == "triggered"]
        for a in triggered:
            r = l2_results[a]
            d = r.get("diagnoses", [{}])[0] if r.get("diagnoses") else {}
            label = l2_metrics["detail"].get(a, "?")
            print(f"    [{label}] {a}: rel={d.get('reliability_score','?')} sev={d.get('severity_score','?')} pri={d.get('priority_score','?')}")

        # Print FN (missed expected)
        for a, lab in l2_metrics["detail"].items():
            if lab == "FN":
                print(f"    [FN] {a}: expected but not triggered")

        print(f"    L1 recall={l1_metrics['recall_at_l1']:.2f}  "
              f"L2 P={l2_metrics['precision_at_l2']:.2f} "
              f"R={l2_metrics['recall_at_l2']:.2f} "
              f"F1={l2_metrics['f1_at_l2']:.2f}  "
              f"TP={l2_metrics['tp']} FP={l2_metrics['fp']} FN={l2_metrics['fn']}")

        result["modes"][mode] = {
            "l1_agents_run": len(l1_status),
            "l2_triggered": triggered,
            "l1_metrics": l1_metrics,
            "l2_metrics": l2_metrics,
        }

    return result

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    filter_mode = None
    filter_ids: list[str] = []

    for a in args:
        if a == "--apriori":      filter_mode = "apriori"
        elif a == "--aposteriori": filter_mode = "aposteriori"
        elif a.startswith("DS"):  filter_ids.append(a)

    # Collect datasets
    all_datasets = sorted(DATASETS_DIR.iterdir())
    datasets = []
    for d in all_datasets:
        if not d.is_dir() or d.name in ("baseA", "baseB"): continue
        if filter_ids and not any(d.name.startswith(fid) for fid in filter_ids): continue
        manifest_p = d / "manifest.json"
        if not manifest_p.exists(): continue
        if filter_mode:
            m = json.loads(manifest_p.read_text(encoding="utf-8-sig")).get("mode", "both")
            if m != "both" and m != filter_mode: continue
        datasets.append(d)

    print("=" * 60)
    print(f"  DATASET EVALUATION  ({len(datasets)} datasets)")
    print("=" * 60)

    all_results = []
    for ds_dir in datasets:
        try:
            r = evaluate_dataset(ds_dir)
        except Exception as e:
            print(f"  ERROR on {ds_dir.name}: {e}")
            r = {"dataset_id": ds_dir.name, "error": str(e)}
        all_results.append(r)

    # Restore noria-0.2
    print(f"\n{'='*60}")
    restore_noria()

    # Summary table
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Dataset':<45} {'Mode':<14} {'L2 P':>6} {'L2 R':>6} {'L2 F1':>7} {'TP/FP/FN'}")
    print("  " + "─" * 90)
    for r in all_results:
        if "error" in r:
            print(f"  {r['dataset_id']:<45}  ERROR: {r['error']}")
            continue
        for mode, m in r.get("modes", {}).items():
            lm = m["l2_metrics"]
            print(f"  {r['dataset_id']:<45} {mode:<14} "
                  f"{lm['precision_at_l2']:>6.2f} {lm['recall_at_l2']:>6.2f} "
                  f"{lm['f1_at_l2']:>7.2f}  "
                  f"{lm['tp']}/{lm['fp']}/{lm['fn']}")

    out = PROJECT_ROOT / "eval_results.json"
    out.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Full results saved to {out.name}")


if __name__ == "__main__":
    main()
