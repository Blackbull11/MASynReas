# DS10_apriori_mixed_two_true_diagnoses

## Purpose

Two independent apriori diagnosis families coexist in the same graph. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `apriori`
- Mutation type: `mixed_apriori_multi_diagnosis`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- `baseA:module_monitoring_dashboard`

### Removed Relations
- `noria:resourceForApplication from baseA:res_customer_vm_02 to baseA:app_customer_portal`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `6`
- Expected Level-2 diagnoses: `2`

### Expected Level-1 Agents
- `apriori/structural/criticality_structural_weakness_detector`
- `apriori/structural/missing_redundancy_detector`
- `apriori/functional/application_without_module_detector`
- `apriori/functional/over_concentrated_service_detector`
- `apriori/functional/service_without_application_detector`
- `apriori/functional/service_without_resource_coverage_detector`

### Expected Level-2 Diagnosers
- `apriori/critical_service_exposure_diagnoser`
- `apriori/functional_mapping_gap_diagnoser`

## KPI Objectives

- Primary focus: `precision_l2`, with diagnosis matching against the expected Level-2 outputs.
- In the current profile, this is mostly followed through `diagnosis_hit` and the list of missed expected diagnoses.
- Primary focus: `top1_accuracy`.
- Reference target: `family_contribution_analysis`.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS10_apriori_mixed_two_true_diagnoses/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS10_apriori_mixed_two_true_diagnoses/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS10_apriori_mixed_two_true_diagnoses/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS10_apriori_mixed_two_true_diagnoses/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
