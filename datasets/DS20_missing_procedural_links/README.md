# DS20 Missing Procedural Links

## Purpose

This scenario removes ticket-event links on two incident chains. The incidents remain visible, but the procedural traceability layer is weakened.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Remove trigger and relation links from the customer and workforce tickets.
- Keep the events and the tickets themselves.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- missing_data_robustness
- traceability_robustness

## Expected Level 1 Signals

- aposteriori/procedural/incident_without_ticket_detector
- aposteriori/procedural/ticket_without_linked_event_detector

## Expected Level 2 Diagnoses

- aposteriori/traceability_breakdown_diagnoser

## Notes

- The expected level-2 outcome is traceability breakdown.
- This scenario is useful for robustness comparisons against complete incident chains.
