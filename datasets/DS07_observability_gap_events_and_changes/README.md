# DS07_observability_gap_events_and_changes

## Purpose

Observability and temporal completeness are degraded across events and changes. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `apriori`
- Mutation type: `observability_gap`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseA:event_obs_missing_timestamp`
- `baseA:event_obs_missing_related`

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- `noria:changeRequestActualEndTime on baseA:change_switch_firmware_window`
- `noria:changeRequestActualEndTime on baseA:change_monitoring_patch`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `4`
- Expected Level-2 diagnoses: `1`

### Expected Level-1 Agents
- `apriori/dynamic/change_without_effective_time_detector`
- `apriori/dynamic/event_without_related_element_detector`
- `apriori/dynamic/event_without_timestamp_detector`

### Expected Level-2 Diagnosers
- `apriori/observability_gap_diagnoser`

## KPI Objectives

- Primary focus: `precision_l2`, with diagnosis matching against the expected Level-2 outputs.
- In the current profile, this is mostly followed through `diagnosis_hit` and the list of missed expected diagnoses.
- Campaign-level focus: future calibration of `reliability_score` once enough runs are accumulated.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS07_observability_gap_events_and_changes/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS07_observability_gap_events_and_changes/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS07_observability_gap_events_and_changes/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS07_observability_gap_events_and_changes/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
