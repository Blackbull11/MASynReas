# DS12_change_induced_incident_basic

## Purpose

A recent change is followed by a high-severity incident on the same element. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `baseB`
- Execution mode: `aposteriori`
- Mutation type: `change_induced_incident`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseB:change_customer_hotfix`
- `baseB:event_customer_post_change`
- `baseB:ticket_customer_post_change`

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- No relation removal in this scenario.

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `3`
- Expected Level-2 diagnoses: `1`

### Expected Level-1 Agents
- `aposteriori/dynamic/change_followed_by_incident_detector`
- `aposteriori/dynamic/change_overlap_conflict`
- `aposteriori/dynamic/critical_event_ticket_escalation_detector`

### Expected Level-2 Diagnosers
- `aposteriori/change_induced_incident_diagnoser`

## KPI Objectives

- Primary focus: `precision_l2`, with diagnosis matching against the expected Level-2 outputs.
- In the current profile, this is mostly followed through `diagnosis_hit` and the list of missed expected diagnoses.
- Primary focus: `top1_accuracy`.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS12_change_induced_incident_basic/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS12_change_induced_incident_basic/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS12_change_induced_incident_basic/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS12_change_induced_incident_basic/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
