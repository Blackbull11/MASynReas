# DS19_missing_data_structural_and_temporal

## Purpose

Structural and temporal information is degraded without creating a full diagnosis. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `baseB`
- Execution mode: `both`
- Mutation type: `missing_data_robustness`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- `baseB:if_billing_api_02`

### Removed Relations
- `noria:loggingTime on baseB:event_monitoring_warning`
- `noria:eventRelatedElement on baseB:event_workforce_warning`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `3`
- Expected Level-2 diagnoses: `0`

### Expected Level-1 Agents
- `apriori/structural/missing_interface_detector`
- `apriori/dynamic/event_without_related_element_detector`
- `apriori/dynamic/event_without_timestamp_detector`

### Expected Level-2 Diagnosers
- No Level-2 diagnoser should emit a diagnosis.

## KPI Objectives

- Campaign-level focus: compare this degraded scenario with its fuller counterpart.
- Primary focus: `l2_activation_correctness` and correct non-activation on weak evidence.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS19_missing_data_structural_and_temporal/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS19_missing_data_structural_and_temporal/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS19_missing_data_structural_and_temporal/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS19_missing_data_structural_and_temporal/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
