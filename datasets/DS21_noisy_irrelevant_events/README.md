# DS21_noisy_irrelevant_events

## Purpose

Benign extra events are injected without strong diagnosis value. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `quiescentB`
- Execution mode: `aposteriori`
- Mutation type: `noise_irrelevant_events`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseB:event_noise_probe_01`
- `baseB:event_noise_probe_02`
- `baseB:event_noise_probe_03`

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- No relation removal in this scenario.

### Noise Additions
- `Three benign events on a non-service resource`

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `1`
- Expected Level-2 diagnoses: `0`

### Expected Level-1 Agents
- `aposteriori/functional/resource_event_without_service_impact_detector`

### Expected Level-2 Diagnosers
- No Level-2 diagnoser should emit a diagnosis.

## KPI Objectives

- Campaign-level focus: compare this noisy scenario with its cleaner counterpart.
- Reference target: `ranking_stability`.
- Secondary timing focus: noisy graphs should remain operationally manageable.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS21_noisy_irrelevant_events/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS21_noisy_irrelevant_events/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS21_noisy_irrelevant_events/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS21_noisy_irrelevant_events/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
