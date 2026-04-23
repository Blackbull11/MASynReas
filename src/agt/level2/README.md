# Level 2 - Diagnosis Agents

The level-2 layer is the deterministic diagnosis layer of MASynReas.
It consumes the JSON outputs produced by level-1 agents, correlates them on
shared anchors, and writes explicit diagnosis files under `results/level2/`.

## Architecture

- `src/agt/level2/apriori`
  Contains the level-2 agents that diagnose weaknesses before incidents.
- `src/agt/level2/aposteriori`
  Contains the level-2 agents that interpret anomalies after incidents.
- `src/agt/level2/common.py`
  Shared deterministic utilities for loading level-1 outputs, correlating anchors,
  computing scores, and exporting standardized JSON payloads.
- `src/agt/level2/level2_controller.asl`
  Waits until all level-1 agents of the selected mode have finished, then launches
  the matching level-2 catalogue.

## A Priori Catalogue

- `structural_fragility_diagnoser`
- `critical_service_exposure_diagnoser`
- `observability_gap_diagnoser`
- `procedural_unreadiness_diagnoser`
- `functional_mapping_gap_diagnoser`

## A Posteriori Catalogue

- `single_point_of_failure_diagnoser`
- `change_induced_incident_diagnoser`
- `service_cascade_diagnoser`
- `traceability_breakdown_diagnoser`
- `unstable_component_diagnoser`
- `application_support_failure_diagnoser`
- `local_infrastructure_cluster_diagnoser`

## Execution Logic

1. The mode selected in `mas.properties` activates the corresponding level-1 family agents.
2. `level2_controller` waits for the completion of all selected level-1 scripts.
3. The controller launches only the level-2 catalogue matching the selected mode.
4. Each level-2 agent reads the relevant level-1 JSON files, checks its activation rule, correlates evidence, and exports one diagnosis JSON file.
5. In `apriori` mode, the MAS stops automatically after the five level-2 a priori agents have finished.

## Output Format

Each level-2 agent writes a JSON object to `results/level2/<mode>/<agent>.json`.

```json
{
  "agent": "service_cascade_diagnoser",
  "mode": "aposteriori",
  "activation_status": "triggered",
  "reason": "Activation conditions satisfied around Service 'SVC_TOY_DBAccess'.",
  "diagnoses": [
    {
      "diagnosis_id": "L2-P3-001",
      "diagnosis_type": "service_cascade",
      "mode": "aposteriori",
      "target_type": "Service",
      "target_id": "https://w3id.org/noria/object/SVC_TOY_DBAccess",
      "reliability_score": 81,
      "severity_score": 74,
      "priority_score": 78,
      "evidence": [],
      "severity_factors": {},
      "explanation": "...",
      "recommended_action": "..."
    }
  ]
}
```

If an agent is not triggered, it still writes an explicit file with:
- `activation_status: "not_triggered"`
- a human-readable `reason`
- an empty `diagnoses` list
