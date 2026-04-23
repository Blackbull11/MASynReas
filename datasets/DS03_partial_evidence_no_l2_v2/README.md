# DS03_partial_evidence_no_l2_v2

## Purpose

Multi-signal weak evidence without coherent level-2 anchor. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `both`
- Mutation type: `multi_signal_weak_evidence`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseA:event_missing_timestamp`

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- `noria:resourceManagedBy on baseA:res_access_switch_02`
- `noria:changeRequestActualEndTime on baseA:change_monitoring_patch`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `3`
- Expected Level-2 diagnoses: `0`

### Expected Level-1 Agents
- `apriori/structural/unmanaged_resource_detector`
- `apriori/dynamic/change_without_effective_time_detector`
- `apriori/dynamic/event_without_timestamp_detector`

### Expected Level-2 Diagnosers
- No Level-2 diagnoser should emit a diagnosis.

## KPI Objectives

- Primary focus: `l2_activation_correctness` and correct non-activation on weak evidence.
- Reference target: `false_positive_resistance_under_multi_signal_conditions`.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS03_partial_evidence_no_l2_v2/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS03_partial_evidence_no_l2_v2/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS03_partial_evidence_no_l2_v2/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS03_partial_evidence_no_l2_v2/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
