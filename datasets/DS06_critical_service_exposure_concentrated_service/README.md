# DS06_critical_service_exposure_concentrated_service

## Purpose

A stronger critical service exposure case on the same business chain. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `apriori`
- Mutation type: `critical_support_concentration_strong`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- `baseA:if_customer_vm_01`

### Removed Relations
- `noria:resourceForApplication from baseA:res_customer_vm_02 to baseA:app_customer_portal`
- `noria:resourceManagedBy on baseA:res_customer_vm_01`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `5`
- Expected Level-2 diagnoses: `1`

### Expected Level-1 Agents
- `apriori/structural/criticality_structural_weakness_detector`
- `apriori/structural/missing_interface_detector`
- `apriori/structural/missing_redundancy_detector`
- `apriori/structural/unmanaged_resource_detector`
- `apriori/functional/over_concentrated_service_detector`

### Expected Level-2 Diagnosers
- `apriori/critical_service_exposure_diagnoser`

## KPI Objectives

- Comparative focus: severity differences should be visible across paired scenarios.
- Comparative focus: priority ordering should remain consistent across paired scenarios.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS06_critical_service_exposure_concentrated_service/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS06_critical_service_exposure_concentrated_service/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS06_critical_service_exposure_concentrated_service/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS06_critical_service_exposure_concentrated_service/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
