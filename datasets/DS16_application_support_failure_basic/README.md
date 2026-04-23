# DS16_application_support_failure_basic

## Purpose

An incidented application loses its visible technical support mapping. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `baseB`
- Execution mode: `aposteriori`
- Mutation type: `application_support_failure`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- `noria:resourceForApplication on baseB:res_billing_api_01`
- `noria:resourceForApplication on baseB:res_billing_api_02`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `2`
- Expected Level-2 diagnoses: `1`

### Expected Level-1 Agents
- `aposteriori/structural/application_mapping_inconsistency_detector`
- `aposteriori/functional/application_incident_without_resource_detector`

### Expected Level-2 Diagnosers
- `aposteriori/application_support_failure_diagnoser`

## KPI Objectives

- Primary focus: `precision_l2`, with diagnosis matching against the expected Level-2 outputs.
- In the current profile, this is mostly followed through `diagnosis_hit` and the list of missed expected diagnoses.
- Reference target: `family_contribution_analysis`.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS16_application_support_failure_basic/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS16_application_support_failure_basic/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS16_application_support_failure_basic/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS16_application_support_failure_basic/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
