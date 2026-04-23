# DS09_functional_mapping_gap_application_chain

## Purpose

A service loses its visible application-module mapping chain. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `apriori`
- Mutation type: `functional_mapping_gap`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- `baseA:module_customer_portal`

### Removed Relations
- No relation removal in this scenario.

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `3`
- Expected Level-2 diagnoses: `1`

### Expected Level-1 Agents
- `apriori/functional/application_without_module_detector`
- `apriori/functional/service_without_application_detector`
- `apriori/functional/service_without_resource_coverage_detector`

### Expected Level-2 Diagnosers
- `apriori/functional_mapping_gap_diagnoser`

## KPI Objectives

- Primary focus: `precision_l2`, with diagnosis matching against the expected Level-2 outputs.
- In the current profile, this is mostly followed through `diagnosis_hit` and the list of missed expected diagnoses.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS09_functional_mapping_gap_application_chain/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS09_functional_mapping_gap_application_chain/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS09_functional_mapping_gap_application_chain/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS09_functional_mapping_gap_application_chain/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
