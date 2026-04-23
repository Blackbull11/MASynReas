# DS08_procedural_unreadiness_basic

## Purpose

Operational process readiness is incomplete before any incident diagnosis. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `apriori`
- Mutation type: `procedural_unreadiness`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseA:event_procedural_gap`
- `baseA:ticket_procedural_gap`

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- `noria:plannedStartDate on baseA:change_switch_firmware_window`
- `noria:plannedEndDate on baseA:change_switch_firmware_window`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `4`
- Expected Level-2 diagnoses: `1`

### Expected Level-1 Agents
- `apriori/procedural/change_request_without_scheduled_time_detector`
- `apriori/procedural/procedure_not_linked_to_resource_type_detector`
- `apriori/procedural/ticket_without_assigned_procedure_detector`

### Expected Level-2 Diagnosers
- `apriori/procedural_unreadiness_diagnoser`

## KPI Objectives

- Primary focus: `precision_l2`, with diagnosis matching against the expected Level-2 outputs.
- In the current profile, this is mostly followed through `diagnosis_hit` and the list of missed expected diagnoses.
- Reference target: `family_contribution_analysis`.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS08_procedural_unreadiness_basic/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS08_procedural_unreadiness_basic/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS08_procedural_unreadiness_basic/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS08_procedural_unreadiness_basic/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
