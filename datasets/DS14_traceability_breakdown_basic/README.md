# DS14_traceability_breakdown_basic

## Purpose

The event-to-ticket traceability chain is broken for one incident. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `baseB`
- Execution mode: `aposteriori`
- Mutation type: `traceability_breakdown`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- `noria:troubleTicketTrigger on baseB:ticket_billing_warning`
- `dcterms:relation on baseB:ticket_billing_warning`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `2`
- Expected Level-2 diagnoses: `1`

### Expected Level-1 Agents
- `aposteriori/procedural/incident_without_ticket_detector`
- `aposteriori/procedural/ticket_without_linked_event_detector`

### Expected Level-2 Diagnosers
- `aposteriori/traceability_breakdown_diagnoser`

## KPI Objectives

- Primary focus: `precision_l2`, with diagnosis matching against the expected Level-2 outputs.
- In the current profile, this is mostly followed through `diagnosis_hit` and the list of missed expected diagnoses.
- Primary focus: traceability and evidence transparency should remain empty but coherent.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS14_traceability_breakdown_basic/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS14_traceability_breakdown_basic/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS14_traceability_breakdown_basic/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS14_traceability_breakdown_basic/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
