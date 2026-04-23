"""
baseline_monoagent.py

Simulates a single-agent sequential baseline: runs all level-1 detector
scripts one after the other in a single process, without JaCaMo.

Measures:
  - Individual script execution times
  - Total sequential time (sum)
  - Theoretical parallel time (max of individual times, i.e. best-case MAS)
  - Speedup ratio: sequential / parallel

Usage:
    python -X utf8 baseline_monoagent.py [apriori|aposteriori|both]

Output:
    baseline_results.json
"""

import json
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable
AGENTS_ROOT = PROJECT_ROOT / "src" / "agt"


def find_scripts(mode: str) -> list[Path]:
    scripts = []
    for path in sorted(AGENTS_ROOT.rglob("*.py")):
        if "__pycache__" in str(path):
            continue
        if "level2" in str(path):
            continue
        if mode in path.parts:
            scripts.append(path)
    return scripts


def run_script(script: Path) -> tuple[int, float]:
    t0 = time.perf_counter()
    proc = subprocess.run(
        [PYTHON, str(script)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )
    return proc.returncode, (time.perf_counter() - t0) * 1000


def run_mode(mode: str) -> dict:
    scripts = find_scripts(mode)
    print(f"\n  [SEQUENTIAL / {mode.upper()}] {len(scripts)} script(s)")
    print(f"  {'Script':<55} {'ms':>8}  Status")
    print("  " + "-" * 72)

    timings = []
    for script in scripts:
        rel = str(script.relative_to(PROJECT_ROOT))
        code, ms = run_script(script)
        status = "OK" if code == 0 else f"FAIL({code})"
        print(f"  {rel:<55} {ms:>7.0f}ms  {status}")
        timings.append({"script": rel, "duration_ms": round(ms, 1), "ok": code == 0})

    durations = [t["duration_ms"] for t in timings if t["ok"]]
    seq_ms = sum(durations)
    par_ms = max(durations) if durations else 0
    speedup = seq_ms / par_ms if par_ms > 0 else 1.0

    print(f"\n  Sequential total : {seq_ms:,.0f} ms  ({seq_ms/1000:.1f}s)")
    print(f"  Theoretical parallel (max): {par_ms:,.0f} ms  ({par_ms/1000:.1f}s)")
    print(f"  Speedup (seq/par)          : {speedup:.1f}x")

    return {
        "mode": mode,
        "n_scripts": len(scripts),
        "scripts": timings,
        "sequential_ms": round(seq_ms, 1),
        "theoretical_parallel_ms": round(par_ms, 1),
        "speedup": round(speedup, 2),
        "slowest_script": max(timings, key=lambda t: t["duration_ms"])["script"] if timings else None,
    }


def main():
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "both"
    modes = ["apriori", "aposteriori"] if mode_arg == "both" else [mode_arg]

    print("=" * 60)
    print("  BASELINE MONO-AGENT (sequential)")
    print("=" * 60)

    results = {}
    for mode in modes:
        results[mode] = run_mode(mode)

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  {'Mode':<14} {'Scripts':>8} {'Sequential':>14} {'Parallel (th.)':>16} {'Speedup':>10}")
    print("  " + "-" * 68)
    for mode, r in results.items():
        print(f"  {mode:<14} {r['n_scripts']:>8} "
              f"{r['sequential_ms']:>12.0f}ms "
              f"{r['theoretical_parallel_ms']:>14.0f}ms "
              f"{r['speedup']:>9.1f}x")

    out = PROJECT_ROOT / "baseline_results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Results saved to {out.name}")


if __name__ == "__main__":
    main()
