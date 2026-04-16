# Multi-agent-Synergistic-Reasoning
Common Scientific Project about "Multi-agent Synergistic Reasoning" in collaboration with Orange Research

## Architecture

The system is a JaCaMo multi-agent system that performs automated network diagnostics on the NORIA knowledge graph (telecom ontology). It uses a **coordinator-worker** pattern:

- **3 worker agents** run SPARQL detection scripts in parallel against a Virtuoso endpoint (`localhost:8890`)
- **1 coordinator agent** collects results, computes a severity level, writes a structured report, then calls a local LLM to generate a narrative diagnosis
- Results are written to `diagnostic_noria.txt`

### Agents
| Agent | Script | Role |
|---|---|---|
| `critical_alarm_agent` | `detection_major.py` | Finds major alarms with a repair plan |
| `propagation_agent` | `detection_propagation.py` | Detects fault propagation across network links |
| `unhandled_agent` | `detection_unhandled.py` | Finds major alarms with no repair plan |
| `coordinator` | `coordinator_agent.asl` | Aggregates results, diagnoses, writes report |

### Severity levels
| Level | Condition |
|---|---|
| CRITIQUE | Propagation + unhandled alarms |
| MAJEURE | Propagation only |
| ELEVEE | Unhandled alarms only |
| NORMALE | Critical alarms with repair plan |
| OK | Nothing detected |

## Requirements

### Java / JaCaMo
- JaCaMo CLI (`jacamo` command available in PATH)
- Java 11+

### Python
- Python 3.8+
- `requests` library: `pip install requests`

### SPARQL endpoint
- Virtuoso running on `http://localhost:8890/sparql` with the NORIA knowledge graph loaded

### Ollama (required for LLM narrative)
The 5th step of the diagnosis generates a natural language narrative using a local LLM via [Ollama](https://ollama.com).

**Each team member must install Ollama independently — it runs locally and is not shared.**

1. Download and install Ollama from `ollama.com/download`
2. Pull the model:
   ```bash
   ollama pull llama3.2:3b
   ```
3. Ollama starts automatically as a background service after installation. If needed, start it manually:
   ```bash
   ollama serve
   ```

To use a different model, change line 7 of `diagnosis_llm.py`:
```python
MODEL = "llama3.2:3b"  # change to "mistral", "qwen2.5:3b", etc.
```

## Running

```bash
jacamo multiagentSystem_v2.jcm
```

Output is written to `diagnostic_noria.txt`.
