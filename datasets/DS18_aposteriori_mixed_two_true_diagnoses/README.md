# DS18_aposteriori_mixed_two_true_diagnoses

## Purpose

Two independent aposteriori diagnosis families coexist. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `baseB`
- Execution mode: `aposteriori`
- Mutation type: `mixed_aposteriori_multi_diagnosis`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseB:event_monitor_down`
- `baseB:event_monitor_up`
- `baseB:event_monitor_timeout`
- `baseB:event_monitor_timeout_repeat`
- `baseB:ticket_monitor_resolved_old`
- `baseB:ticket_monitor_active_new`

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- No relation removal in this scenario.

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `5`
- Expected Level-2 diagnoses: `2`

### Expected Level-1 Agents
- `aposteriori/dynamic/event_burst_detector`
- `aposteriori/dynamic/flapping_state_detector`
- `aposteriori/dynamic/reopened_incident_detector`
- `aposteriori/functional/cascading_service_failure_detector`
- `aposteriori/functional/hidden_service_dependency_detector`

### Expected Level-2 Diagnosers
- `aposteriori/service_cascade_diagnoser`
- `aposteriori/unstable_component_diagnoser`

## KPI Objectives

- Primary focus: `precision_l2`, with diagnosis matching against the expected Level-2 outputs.
- In the current profile, this is mostly followed through `diagnosis_hit` and the list of missed expected diagnoses.
- Primary focus: `top1_accuracy`.
- Reference target: `mrr`.
- Reference target: `family_contribution_analysis`.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS18_aposteriori_mixed_two_true_diagnoses/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS18_aposteriori_mixed_two_true_diagnoses/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS18_aposteriori_mixed_two_true_diagnoses/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS18_aposteriori_mixed_two_true_diagnoses/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
