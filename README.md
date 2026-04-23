# MASynReas

MASynReas is a multi-agent system for anomaly diagnosis in a knowledge graph representing an ICT or telecommunication network.

The project is implemented with:
- JaCaMo for the multi-agent system
- Python scripts for SPARQL query execution
- OpenLink Virtuoso as the SPARQL endpoint
- NORIA-O as the ontology used to structure the graph

## Architecture

The system is organized in three layers:

- **Level 1 — Detector agents**: one elementary pattern per agent, one SPARQL query per agent, one JSON result file per agent
- **Level 2 — Diagnoser agents**: deterministic aggregation of level-1 outputs into higher-level diagnoses
- **Level 3 — Narrative synthesis**: a local LLM synthesizes a natural-language diagnosis from level-1+2 outputs (evaluated via ablation study; not wired into the JaCaMo MAS)

### Level 1 families

| Family | Apriori agents | Aposteriori agents |
|--------|:--------------:|:-----------------:|
| Structural | 10 | 7 |
| Dynamic | 3 | 12 |
| Functional | 7 | 9 |
| Procedural | 3 | 3 |

Level 1 currently represents **54 detector agents**.

### Level 2 catalogue

Level 2 is no longer a small flat prototype. It is now organized by execution mode:

- `src/agt/level2/apriori`
- `src/agt/level2/aposteriori`

#### A priori diagnosers

- `structural_fragility_diagnoser`
- `critical_service_exposure_diagnoser`
- `observability_gap_diagnoser`
- `procedural_unreadiness_diagnoser`
- `functional_mapping_gap_diagnoser`

#### A posteriori diagnosers

- `single_point_of_failure_diagnoser`
- `change_induced_incident_diagnoser`
- `service_cascade_diagnoser`
- `traceability_breakdown_diagnoser`
- `unstable_component_diagnoser`
- `application_support_failure_diagnoser`
- `local_infrastructure_cluster_diagnoser`

Level 2 therefore currently contains **12 diagnoser agents**.

Each level-2 agent:
- reads a selected set of level-1 JSON result files
- checks deterministic activation conditions
- correlates evidence on shared anchors
- computes reliability, severity, and priority scores
- writes one diagnosis JSON file under `results/level2/<mode>/`

See [src/agt/level2/README.md](src/agt/level2/README.md) for the detailed level-2 architecture.

## Execution Modes

The MAS can be launched in two modes:

- `apriori`: diagnoses weaknesses independently from any explicit incident context
- `aposteriori`: diagnoses anomaly causes and propagation after incidents, events, or tickets exist

The selected mode is configured in `mas.properties`:

```properties
mode=apriori
python.path=C:/path/to/python.exe
```

Accepted values are `apriori` and `aposteriori`.

## Running the MAS

From the project root:

```powershell
jacamo multiagentSystem.jcm
```

Execution flow:

1. The selected mode activates the corresponding level-1 agents.
2. Level-1 agents write their JSON results in `results/<family>/<mode>/`.
3. `level2_controller` waits for all level-1 scripts of the selected mode.
4. The controller launches only the level-2 diagnosers of the same mode.

Current mode-specific behavior:

- In `apriori` mode, the MAS stops automatically after the 5 level-2 a priori diagnosers complete.
- In `aposteriori` mode, the 7 level-2 a posteriori diagnosers run after the full level-1 catalogue of that mode.

## Running Experiments

```powershell
python -X utf8 run_all_detectors.py both
python -X utf8 complementarity_table.py

# Sequential baseline (speedup measurement)
python -X utf8 baseline_monoagent.py both

# Ablation study — LLM value added by each MAS layer (~25 min)
python -X utf8 ablation_study.py

# LLM baseline comparison — give the full graph to a single LLM
# Requires Virtuoso + Ollama, or noria_graph.ttl + HuggingFace transformers
python -X utf8 llm_detector_baseline.py both both
```

See `EXPERIMENTS_README.md` for the experiment-oriented documentation.

## Requirements

### Java / JaCaMo

- JaCaMo CLI available in `PATH`
- Java 11+

### Python

- Python 3.8+
- `requests`
- `SPARQLWrapper`

### SPARQL endpoint

- Virtuoso running on `http://localhost:8890/sparql`
- NORIA-O dataset loaded in the endpoint

### Level 3 synthesis

If you use the narrative synthesis layer, configure the local LLM runtime expected by the project.

### LLM baseline on a GPU server (no Virtuoso needed)

`llm_detector_baseline.py` auto-detects the available backend:
- If Ollama is running locally → uses it (any pulled model)
- Otherwise → loads `mistralai/Mistral-7B-Instruct-v0.3` via HuggingFace transformers

To run on a remote GPU server, copy three files and install one dependency:
```bash
scp llm_detector_baseline.py noria_graph.ttl user@server:~/baseline/
scp -r results/ user@server:~/baseline/
ssh user@server "pip install --user transformers accelerate torch requests protobuf sentencepiece"
ssh user@server "cd ~/baseline && HF_HOME=/tmp/hf_cache python3 llm_detector_baseline.py both both"
```

## Main entry files

- [multiagentSystem.jcm](multiagentSystem.jcm)
- [mas.properties](mas.properties)
- [src/env/env/PythonExecArtifact.java](src/env/env/PythonExecArtifact.java)
- [src/agt/level2/README.md](src/agt/level2/README.md)
- [EXPERIMENTS_README.md](EXPERIMENTS_README.md)
