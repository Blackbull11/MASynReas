# DS01_clean_baseA

## Purpose

Clean control scenario derived from Base A. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `both`
- Mutation type: `quiescent_clean_slice`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- `baseA:event_customer_warning`
- `baseA:event_monitoring_warning`
- `baseA:ticket_customer_warning`
- `baseA:ticket_monitoring_warning`

### Removed Relations
- No relation removal in this scenario.

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `0`
- Expected Level-2 diagnoses: `0`

### Expected Level-1 Agents
- No Level-1 agent should return a non-zero result.

### Expected Level-2 Diagnosers
- No Level-2 diagnoser should emit a diagnosis.

## KPI Objectives

- Primary focus: `clean_control_success` and false-positive resistance.
- Primary focus: `l2_activation_correctness` and correct non-activation on weak evidence.
- Primary focus: `end_to_end_runtime`, `mean_runtime_l1`, and `mean_runtime_l2`.
- Primary focus: traceability and evidence transparency should remain empty but coherent.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS01_clean_baseA/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS01_clean_baseA/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS01_clean_baseA/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS01_clean_baseA/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
