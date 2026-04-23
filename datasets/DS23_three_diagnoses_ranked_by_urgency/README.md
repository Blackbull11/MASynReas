# DS23_three_diagnoses_ranked_by_urgency

## Purpose

Three true diagnoses coexist with different operational urgency. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- Source variant: `baseB`
- Execution mode: `aposteriori`
- Mutation type: `ranking_three_true_diagnoses`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- `baseB:event_firewall_major`
- `baseB:ticket_firewall_major`
- `baseB:event_monitor_down`
- `baseB:event_monitor_up`
- `baseB:event_monitor_timeout`
- `baseB:event_monitor_timeout_repeat`
- `baseB:ticket_monitor_resolved_old`
- `baseB:ticket_monitor_active_new`

### Removed Entities
- `baseB:if_workforce_vm_01`
- `baseB:if_firewall_01_port_02`
- `baseB:link_workforce_vm_01_to_firewall_01`
- `baseB:if_monitor_vm_01`

### Removed Relations
- `noria:troubleTicketTrigger on baseB:ticket_billing_warning`
- `dcterms:relation on baseB:ticket_billing_warning`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `9`
- Expected Level-2 diagnoses: `3`

### Expected Level-1 Agents
- `aposteriori/structural/high_impact_resource_detector`
- `aposteriori/structural/incident_on_incomplete_link_detector`
- `aposteriori/structural/isolated_incident_resource_detector`
- `aposteriori/structural/no_redundancy_incident_detector`
- `aposteriori/dynamic/event_burst_detector`
- `aposteriori/dynamic/flapping_state_detector`
- `aposteriori/dynamic/reopened_incident_detector`
- `aposteriori/procedural/incident_without_ticket_detector`
- `aposteriori/procedural/ticket_without_linked_event_detector`

### Expected Level-2 Diagnosers
- `aposteriori/single_point_of_failure_diagnoser`
- `aposteriori/traceability_breakdown_diagnoser`
- `aposteriori/unstable_component_diagnoser`

### Ranking Expectation
- `aposteriori/single_point_of_failure_diagnoser`
- `aposteriori/unstable_component_diagnoser`
- `aposteriori/traceability_breakdown_diagnoser`

## KPI Objectives

- Primary focus: `top1_accuracy`.
- Reference target: `mrr`.
- Campaign-level focus: future calibration of `priority_score` and urgency ordering.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS23_three_diagnoses_ranked_by_urgency/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS23_three_diagnoses_ranked_by_urgency/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS23_three_diagnoses_ranked_by_urgency/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS23_three_diagnoses_ranked_by_urgency/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
