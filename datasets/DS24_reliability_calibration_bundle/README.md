# DS24_reliability_calibration_bundle

## Purpose

Several diagnosis candidates are present with different evidence strengths. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `quiescentB`
- Execution mode: `both`
- Mutation type: `reliability_calibration_bundle`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseB:event_reliability_gap`

### Removed Entities
- `baseB:if_firewall_02_port_01`
- `baseB:if_firewall_02_port_02`

### Removed Relations
- `noria:changeRequestActualEndTime on baseB:change_switch_maintenance`
- `noria:resourceForApplication on baseB:res_customer_vm_02`
- `noria:resourceManagedBy on baseB:res_firewall_02`
- `seas:subSystemOf on baseB:res_firewall_02`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `8`
- Expected Level-2 diagnoses: `3`

### Expected Level-1 Agents
- `apriori/structural/criticality_structural_weakness_detector`
- `apriori/structural/missing_interface_detector`
- `apriori/structural/missing_parent_resource_detector`
- `apriori/structural/missing_redundancy_detector`
- `apriori/structural/unmanaged_resource_detector`
- `apriori/dynamic/change_without_effective_time_detector`
- `apriori/dynamic/event_without_related_element_detector`
- `apriori/functional/over_concentrated_service_detector`

### Expected Level-2 Diagnosers
- `apriori/critical_service_exposure_diagnoser`
- `apriori/observability_gap_diagnoser`
- `apriori/structural_fragility_diagnoser`

### Ranking Expectation
- `apriori/structural_fragility_diagnoser`
- `apriori/critical_service_exposure_diagnoser`
- `apriori/observability_gap_diagnoser`

## KPI Objectives

- Campaign-level focus: future calibration of `reliability_score` once enough runs are accumulated.
- Focus: diagnoses should activate with appropriately graded evidence, not too early or too late.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS24_reliability_calibration_bundle/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS24_reliability_calibration_bundle/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS24_reliability_calibration_bundle/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS24_reliability_calibration_bundle/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
