# MASynReas

MASynReas is a multi-agent system for anomaly diagnosis in a knowledge graph representing an ICT or telecommunication network.

The project is implemented with:
- JaCaMo for the multi-agent system
- Python scripts for SPARQL query execution
- OpenLink Virtuoso as the SPARQL endpoint
- NORIA-O as the ontology used to structure the graph

## Architecture

The system has three layers:

- **Level 1 — Detector agents** (54 agents across 4 families): each runs a SPARQL query against Virtuoso and writes a JSON result to `results/`
- **Level 2 — Diagnoser agents** (4 agents): correlate level-1 results across families to produce structured diagnoses with confidence scores
- **Level 3 — Narrative synthesis**: a local LLM (via Ollama) synthesizes a natural language diagnosis from level-1+2 outputs (evaluated via ablation study; not wired into the JaCaMo MAS)

### Agent families

| Family | Apriori agents | Aposteriori agents |
|--------|:--------------:|:-----------------:|
| Structural | 10 | 7 |
| Dynamic | 3 | 12 |
| Functional | 7 | 9 |
| Procedural | 3 | 3 |

### Level-2 diagnosers

| Agent | Mode | Correlation |
|-------|------|-------------|
| `single_point_of_failure_diagnoser` | aposteriori | 3 structural signals on same resource |
| `change_induced_incident_diagnoser` | aposteriori | dynamic + procedural signals on same change |
| `traceability_breakdown_diagnoser` | aposteriori | incident_without_ticket + ticket_without_event |
| `structural_fragility_diagnoser` | apriori | accumulation of governance weaknesses |

## Execution Modes

The MAS can be launched in two modes:
- `apriori`: detects structural weaknesses independently of any incident context
- `aposteriori`: diagnoses anomalies in an incident context

The selected mode is configured in `mas.properties`:

```properties
mode=apriori
python.path=C:/path/to/python.exe
```

Accepted values: `apriori` or `aposteriori`.

## Running the MAS

From the project root:

```powershell
jacamo multiagentSystem.jcm
```

In `apriori` mode, the MAS stops automatically after all detectors and the level-2 diagnoser complete.  
In `aposteriori` mode, the 3 level-2 diagnosers run after all level-1 detectors complete.

## Running experiments (without JaCaMo)

```powershell
# Run all level-1 detectors directly
python -X utf8 run_all_detectors.py both

# Complementarity table (non-redundancy proof)
python -X utf8 complementarity_table.py

# Sequential baseline (speedup measurement)
python -X utf8 baseline_monoagent.py both

# Ablation study — LLM value added by each MAS layer (~25 min)
python -X utf8 ablation_study.py
```

See `EXPERIMENTS_README.md` for full results and analysis.

## Requirements

### Java / JaCaMo
- JaCaMo CLI (`jacamo` command available in PATH)
- Java 11+

### Python
- Python 3.8+
- `requests`, `SPARQLWrapper` libraries

### SPARQL endpoint
- Virtuoso running on `http://localhost:8890/sparql` with NORIA-O dataset loaded

### Ollama (for level-3 narrative and ablation study)

1. Download and install Ollama from `ollama.com/download`
2. Pull the models:
   ```bash
   ollama pull llama3.2:3b
   ollama pull llama3.1:8b
   ```
3. Ollama starts automatically as a background service. If needed: `ollama serve`

## Main entry files

- `multiagentSystem.jcm` — main JaCaMo project file
- `mas.properties` — mode and python path configuration
- `src/env/env/PythonExecArtifact.java` — shared artifact that runs Python scripts
- `src/agt/level2/README.md` — level-2 agent documentation
- `EXPERIMENTS_README.md` — experiment results and analysis
