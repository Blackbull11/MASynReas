import json, sys, requests

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
MODEL        = "llama3.2:3b"      # change to "mistral", "qwen2.5:3b", etc.
REPORT_FILE  = "diagnostic_noria.txt"   # narrative is appended here directly
OUTPUT_FILE  = "result_narrative.txt"   # status file required by execPython

RESULT_FILES = {
    "critical":    "result_major.json",
    "propagation": "result_propagation.json",
    "unhandled":   "result_unhandled.json",
}

# ─────────────────────────────────────────────────────────────────────────────
def load_results():
    data = {}
    for key, path in RESULT_FILES.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data[key] = json.load(f)
        except Exception as e:
            print(f"[Python LLM] Warning: could not read {path}: {e}")
            data[key] = []
    return data


def build_prompt(data):
    critical    = data["critical"]
    propagation = data["propagation"]
    unhandled   = data["unhandled"]

    sections = []
    if critical:
        sections.append("CRITICAL ALARMS (repair plan exists):\n" +
                        json.dumps(critical, indent=2, ensure_ascii=False))
    if propagation:
        sections.append("NETWORK PROPAGATION (fault spread to neighbors):\n" +
                        json.dumps(propagation, indent=2, ensure_ascii=False))
    if unhandled:
        sections.append("UNHANDLED ALARMS (no repair plan):\n" +
                        json.dumps(unhandled, indent=2, ensure_ascii=False))

    if not sections:
        return None   # nothing to analyse

    body = "\n\n".join(sections)

    return (
        "You are a network operations expert. "
        "Based on the following structured alarm data from a telecom network knowledge graph, "
        "write a concise technical diagnostic narrative in 3-5 sentences. "
        "Focus on: what failed, which resources and teams are involved, how the fault propagated, "
        "and the recommended immediate action. "
        "Be specific — use the resource names, team names, and repair labels from the data. "
        "Do NOT add bullet points or headings, write plain prose only.\n\n"
        + body
        + "\n\nDiagnostic narrative:"
    )


def call_ollama(prompt):
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["response"].strip()


def run():
    print("[Python LLM] Loading alarm data...")
    data = load_results()

    prompt = build_prompt(data)
    if prompt is None:
        narrative = "No alarms detected — the network appears healthy."
        print("[Python LLM] Nothing to analyse, writing default narrative.")
    else:
        print(f"[Python LLM] Calling Ollama ({MODEL})...")
        narrative = call_ollama(prompt)
        print(f"[Python LLM] Narrative generated ({len(narrative)} chars).")

    narrative_flat = " ".join(narrative.split())

    # Append narrative directly to the structured report
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n=== ANALYSE NARRATIVE (LLM) ===\n")
        f.write(narrative_flat + "\n")
    print(f"[Python LLM] Narrative appended to {REPORT_FILE}.")

    # Write status file (required by execPython — it must exist)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("done")
    print(f"[Python LLM] Status written to {OUTPUT_FILE}.")


if __name__ == "__main__":
    run()
