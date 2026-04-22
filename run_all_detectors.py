"""
run_all_detectors.py

Runs all level-1 detector scripts for a given mode (apriori or aposteriori)
directly, bypassing JaCaMo. Useful for testing and for the complementarity table.

Usage:
    python -X utf8 run_all_detectors.py aposteriori
    python -X utf8 run_all_detectors.py apriori
    python -X utf8 run_all_detectors.py both
"""

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
        parts = path.parts
        if mode in parts:
            scripts.append(path)
    return scripts


def run_script(script: Path) -> tuple[int, float, str]:
    t0 = time.perf_counter()
    proc = subprocess.run(
        [PYTHON, str(script)],
        capture_output=True, text=True,
        cwd=PROJECT_ROOT,
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )
    elapsed = (time.perf_counter() - t0) * 1000
    return proc.returncode, elapsed, (proc.stdout + proc.stderr).strip()


def run_mode(mode: str):
    scripts = find_scripts(mode)
    print(f"\n  [{mode.upper()}] {len(scripts)} script(s) found")
    print(f"  {'Script':<55} {'Time':>8}  {'Status'}")
    print("  " + "-" * 75)

    results = []
    for script in scripts:
        rel = script.relative_to(PROJECT_ROOT)
        code, ms, out = run_script(script)
        status = "OK" if code == 0 else f"FAIL({code})"
        print(f"  {str(rel):<55} {ms:>7.0f}ms  {status}")
        results.append({"script": str(rel), "mode": mode, "exit_code": code, "duration_ms": round(ms, 1)})

    ok = sum(1 for r in results if r["exit_code"] == 0)
    print(f"\n  {ok}/{len(results)} scripts succeeded in {sum(r['duration_ms'] for r in results):.0f}ms total")
    return results


def main():
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "aposteriori"
    modes = ["apriori", "aposteriori"] if mode_arg == "both" else [mode_arg]

    print("=" * 60)
    print("  RUN ALL DETECTORS")
    print("=" * 60)

    for mode in modes:
        run_mode(mode)

    print("\n  Done. Results written to results/")


if __name__ == "__main__":
    main()
