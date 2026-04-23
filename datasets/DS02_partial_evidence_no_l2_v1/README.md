# DS02_partial_evidence_no_l2_v1

## Purpose

Weak isolated evidence without convergent level-2 diagnosis. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `both`
- Mutation type: `weak_partial_signals`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseA:event_partial_signal`

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- `noria:changeRequestActualEndTime on baseA:change_switch_firmware_window`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `2`
- Expected Level-2 diagnoses: `0`

### Expected Level-1 Agents
- `apriori/dynamic/change_without_effective_time_detector`
- `apriori/dynamic/event_without_related_element_detector`

### Expected Level-2 Diagnosers
- No Level-2 diagnoser should emit a diagnosis.

## KPI Objectives

- Primary focus: `l2_activation_correctness` and correct non-activation on weak evidence.
- Reference target: `false_positive_resistance`.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS02_partial_evidence_no_l2_v1/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS02_partial_evidence_no_l2_v1/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS02_partial_evidence_no_l2_v1/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS02_partial_evidence_no_l2_v1/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
