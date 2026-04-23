# DS20_missing_procedural_links

## Purpose

Operational artifacts exist but key procedural links are missing. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `baseB`
- Execution mode: `aposteriori`
- Mutation type: `missing_procedural_links`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- `noria:troubleTicketTrigger and dcterms:relation on baseB:ticket_customer_warning`
- `noria:troubleTicketTrigger and dcterms:relation on baseB:ticket_workforce_warning`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `4`
- Expected Level-2 diagnoses: `1`

### Expected Level-1 Agents
- `aposteriori/procedural/incident_without_ticket_detector`
- `aposteriori/procedural/ticket_without_linked_event_detector`

### Expected Level-2 Diagnosers
- `aposteriori/traceability_breakdown_diagnoser`

## KPI Objectives

- Campaign-level focus: compare this degraded scenario with its fuller counterpart.
- Focus: how much traceability and evidence structure survive degraded linkage.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS20_missing_procedural_links/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS20_missing_procedural_links/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS20_missing_procedural_links/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS20_missing_procedural_links/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
