# Level 2 — Correlation and Interpretation Agents

Level-1 agents each detect one elementary anomaly pattern in isolation.
Level-2 agents consume the JSON outputs of multiple level-1 agents,
correlate them on a shared entity (resource, change request, ticket),
and produce a **diagnosis** with a confidence score and a natural-language explanation.

**Level 1 asks:** "Which elementary patterns are present?"
**Level 2 asks:** "What higher-level conclusion do these patterns support together?"

---

## Agents

### `single_point_of_failure_diagnoser` — A Posteriori

A resource is diagnosed as a single point of failure when three independent
structural signals converge on the same URI: it is weakly connected during an incident,
has no redundant counterpart, and supports many dependents.

| Input | Source |
|-------|--------|
| `isolated_incident_resource_results.json` | structural / aposteriori |
| `no_redundancy_incident_results.json` | structural / aposteriori |
| `high_impact_resource_results.json` | structural / aposteriori |

Correlation key: `resource` URI — confidence 1.0 (3/3 signals) or 0.65 (2/3)

---

### `change_induced_incident_diagnoser` — A Posteriori

A change request is the probable root cause of an incident when a temporal signal
(change temporally followed by an incident on a related element) and a procedural
signal (same change linked to multiple incident tickets) both point to the same change URI.

| Input | Source |
|-------|--------|
| `change_followed_by_incident_results.json` | dynamic / aposteriori |
| `change_linked_to_multiple_incidents_results.json` | procedural / aposteriori |

Correlation key: `change` URI — confidence 0.85 (both signals), 0.55/0.45 (single signal)

---

### `traceability_breakdown_diagnoser` — A Posteriori

A systemic traceability failure occurs when incidents produce no tickets AND tickets
have no linked events simultaneously. These two signals cannot be joined on a common
key; their co-presence is the diagnosis: the entire operational traceability chain is broken.

| Input | Source |
|-------|--------|
| `incident_without_ticket_results.json` | procedural / aposteriori |
| `ticket_without_linked_event_results.json` | procedural / aposteriori |

Correlation key: co-presence of both signals — confidence 0.90 (both), 0.55–0.60 (single)

---

### `structural_fragility_diagnoser` — A Priori

A resource is structurally fragile when it accumulates 2 or more independent
governance weaknesses before any incident occurs: orphaned, missing interface,
missing parent, or unmanaged. Such nodes will be very hard to diagnose when
an incident eventually involves them.

| Input | Source |
|-------|--------|
| `orphan_resource_results.json` | structural / apriori |
| `missing_interface_results.json` | structural / apriori |
| `missing_parent_resource_results.json` | structural / apriori |
| `unmanaged_resource_results.json` | structural / apriori |

Correlation key: `resource` URI — confidence 1.0 (4/4), 0.80 (3/4), 0.55 (2/4)

---

## Execution

Level-2 agents are **not triggered by the mode property** like level-1 agents.
They are launched by `level2_controller` once all level-1 detectors have finished,
via `.send(agent, achieve, run)`.

This guarantees that all level-1 result files are written before any level-2
correlation begins.

```
Level 1 (parallel)  ──────────────────────►  python_finished × N
                                                      │
                                              level2_controller
                                                      │
                                          ┌───────────┴───────────┐
                                          ▼           ▼           ▼
                                        SPOF     ChangeInduced  Traceability
                                        (apost.) (apost.)       (apost.)
                                          │
                                 StructuralFragility
                                        (apriori)
```

## Output format

Every level-2 agent writes a JSON array to `results/level2/<mode>/`.
Each entry contains:

```json
{
  "diagnosis_type":  "single_point_of_failure",
  "mode":            "aposteriori",
  "target":          "https://w3id.org/noria/resource/RES_TOY_as2",
  "target_name":     "RES_TOY_as2",
  "evidence":        ["isolated_incident_resource", "no_redundancy_incident"],
  "evidence_count":  2,
  "confidence":      0.65,
  "severity":        "HIGH",
  "explanation":     "Resource RES_TOY_as2 is confirmed as..."
}
```

Empty output (`[]`) means no correlation threshold was reached — not an error.
