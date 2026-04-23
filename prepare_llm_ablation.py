"""
prepare_llm_ablation.py  —  LOCAL phase

For each target dataset:
  1. Loads dataset.ttl into Virtuoso
  2. Runs all aposteriori L1+L2 agents
  3. Exports: raw Turtle, L1 summary, L2 summary, expected diagnoses

Writes llm_ablation_data.json — the self-contained package that
llm_ablation_infer.py (GPU) will read for inference.

Usage:
    python -X utf8 prepare_llm_ablation.py
    python -X utf8 prepare_llm_ablation.py DS11 DS12  # specific datasets
"""

from __future__ import annotations

import json, os, subprocess, sys, time
from pathlib import Path

import requests
from requests.auth import HTTPDigestAuth

PROJECT_ROOT = Path(__file__).resolve().parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR  = PROJECT_ROOT / "results"
PYTHON       = sys.executable

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
        print(f"    WARN HTTP {r.status_code}")

def restore_noria():
    print("  Restoring noria-0.2...", end="", flush=True)
    clear_virtuoso()
    first = True
    for ttl in sorted(NORIA_DUMPS.glob("*.ttl")):
        load_ttl_http(ttl, NR_GRAPH, replace=first)
        first = False
    print(" done")

# ── Agent runners ────────────────────────────────────────────────────────────

def run_l1_agents(mode: str):
    agents_root = PROJECT_ROOT / "src" / "agt"
    for path in sorted(agents_root.rglob("*.py")):
        if "__pycache__" in str(path) or "level2" in str(path):
            continue
        if mode in path.parts:
            subprocess.run([PYTHON, str(path)], capture_output=True, text=True,
                           cwd=PROJECT_ROOT,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=30)

def run_l2_agents(mode: str):
    agents_l2 = PROJECT_ROOT / "src" / "agt" / "level2" / mode
    for script in sorted(agents_l2.glob("*.py")):
        subprocess.run([PYTHON, str(script)], capture_output=True, text=True,
                       cwd=PROJECT_ROOT,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=30)

def collect_l1_results(mode: str) -> dict[str, list]:
    results = {}
    for path in sorted(RESULTS_DIR.rglob("*.json")):
        s = str(path).replace("\\", "/")
        if "level2" in s or "campaign" in s or "metrics" in s or "baseline" in s or "ablation" in s:
            continue
        if f"/{mode}/" in s:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    results[path.stem] = data
            except Exception:
                pass
    return results

def collect_l2_results(mode: str) -> dict[str, dict]:
    results = {}
    l2_dir = RESULTS_DIR / "level2" / mode
    for path in sorted(l2_dir.glob("*.json")):
        try:
            results[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return results

# ── Data exporters ───────────────────────────────────────────────────────────

def _local_name(uri: str) -> str:
    local = uri.rstrip("/").split("/")[-1].split("#")[-1]
    if ":" in local:
        local = local.split(":")[-1]
    return local

def build_l1_summary(l1_results: dict[str, list]) -> str:
    lines = ["Level-1 detector findings (aposteriori):"]
    active = False
    for agent, rows in sorted(l1_results.items()):
        if not rows:
            continue
        active = True
        entities = []
        for row in rows:
            for v in row.values():
                if isinstance(v, dict) and v.get("type") == "uri":
                    entities.append(_local_name(v["value"]))
        entities = list(dict.fromkeys(entities))[:8]
        lines.append(f"  - {agent}: {', '.join(entities)}")
    if not active:
        lines.append("  (no detectors fired — all results empty)")
    return "\n".join(lines)

def build_l2_summary(l2_results: dict[str, dict]) -> str:
    lines = ["Level-2 correlation diagnoses (aposteriori):"]
    active = False
    for agent, result in sorted(l2_results.items()):
        if result.get("activation_status") != "triggered":
            continue
        active = True
        diag = result.get("diagnoses", [{}])[0] if result.get("diagnoses") else {}
        anchor = diag.get("target_name") or diag.get("anchor", "?")
        rel = diag.get("reliability_score", "?")
        sev = diag.get("severity_score", "?")
        pri = diag.get("priority_score", "?")
        lines.append(f"  - {agent}: TRIGGERED  anchor={anchor}  reliability={rel}  severity={sev}  priority={pri}")
    if not active:
        lines.append("  (no diagnosers triggered)")
    return "\n".join(lines)

def get_expected(ds_dir: Path, mode: str) -> list[str]:
    exp_path = ds_dir / "expected_level2.json"
    if not exp_path.exists():
        return []
    exp = json.loads(exp_path.read_text(encoding="utf-8-sig"))
    return [agent for agent, cases in exp.get(mode, {}).items() if cases]

def get_mas_triggered(l2_results: dict[str, dict]) -> list[str]:
    return [k for k, v in l2_results.items() if v.get("activation_status") == "triggered"]

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mode = "aposteriori"

    datasets = []
    for d in sorted(DATASETS_DIR.iterdir()):
        if not d.is_dir() or not (d / "dataset.ttl").exists():
            continue
        if d.name not in TARGET_DATASETS:
            continue
        if args and not any(d.name.startswith(a) for a in args):
            continue
        datasets.append(d)

    print("=" * 64)
    print(f"  PREPARING LLM ABLATION DATA ({len(datasets)} datasets)")
    print("=" * 64)

    all_data = []

    for ds_dir in datasets:
        ds_id = ds_dir.name
        print(f"\n  ── {ds_id}")

        clear_virtuoso()
        print("    Loading TTL...", end="", flush=True)
        load_ttl_http(ds_dir / "dataset.ttl")

        print("  L1...", end="", flush=True)
        t0 = time.perf_counter()
        run_l1_agents(mode)
        l1_results = collect_l1_results(mode)
        active_l1 = sum(1 for v in l1_results.values() if v)
        print(f" {active_l1} active agents  {(time.perf_counter()-t0)*1000:.0f}ms", end="")

        print("  L2...", end="", flush=True)
        t1 = time.perf_counter()
        run_l2_agents(mode)
        l2_results = collect_l2_results(mode)
        mas_triggered = get_mas_triggered(l2_results)
        print(f" {len(mas_triggered)} triggered  {(time.perf_counter()-t1)*1000:.0f}ms")
        if mas_triggered:
            print(f"    MAS triggered: {mas_triggered}")

        graph_ttl    = (ds_dir / "dataset.ttl").read_text(encoding="utf-8-sig")
        l1_summary   = build_l1_summary(l1_results)
        l2_summary   = build_l2_summary(l2_results)
        expected     = get_expected(ds_dir, mode)

        print(f"    Expected: {expected}")

        all_data.append({
            "dataset_id":   ds_id,
            "mode":         mode,
            "expected":     expected,
            "mas_triggered": mas_triggered,
            "graph_ttl":    graph_ttl,
            "l1_summary":   l1_summary,
            "l2_summary":   l2_summary,
        })

    restore_noria()

    out = PROJECT_ROOT / "llm_ablation_data.json"
    out.write_text(json.dumps(all_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Data saved to {out.name}  ({len(all_data)} datasets)")
    print("  Next: scp llm_ablation_data.json llm_ablation_infer.py to jaguar and run --gpu")


if __name__ == "__main__":
    main()
