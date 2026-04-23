# DS22_noisy_duplicate_and_inconsistent_records

## Purpose

Weak inconsistent functional records are introduced without a decisive diagnosis. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `quiescentB`
- Execution mode: `both`
- Mutation type: `noise_duplicate_inconsistent_records`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseB:module_shadow_ops`
- `baseB:res_shadow_probe`

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- No relation removal in this scenario.

### Noise Additions
- `Low-stakes duplicated and inconsistent functional mappings`

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `2`
- Expected Level-2 diagnoses: `0`

### Expected Level-1 Agents
- `apriori/functional/duplicated_functional_mapping_detector`
- `apriori/functional/inconsistent_service_hierarchy_detector`

### Expected Level-2 Diagnosers
- No Level-2 diagnoser should emit a diagnosis.

## KPI Objectives

- Campaign-level focus: compare this noisy scenario with its cleaner counterpart.
- Reference target: `false_positive_sensitivity`.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS22_noisy_duplicate_and_inconsistent_records/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS22_noisy_duplicate_and_inconsistent_records/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS22_noisy_duplicate_and_inconsistent_records/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS22_noisy_duplicate_and_inconsistent_records/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
