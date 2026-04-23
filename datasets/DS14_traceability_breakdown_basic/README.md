# DS14 Traceability Breakdown Basic

## Purpose

This scenario removes the explicit event-ticket links for one incident so that the procedural aposteriori family can detect a traceability breakdown.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Remove the trigger and relation links from aseB:ticket_billing_warning to aseB:event_billing_warning.
- Keep the rest of the billing incident context intact.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- precision_at_l2
- recall_at_l2
- traceability_sanity_check

## Expected Level 1 Signals

- aposteriori/procedural/incident_without_ticket_detector
- aposteriori/procedural/ticket_without_linked_event_detector

## Expected Level 2 Diagnoses

- aposteriori/traceability_breakdown_diagnoser

## Notes

- One event becomes ticketless from the graph perspective.
- One ticket becomes eventless from the graph perspective.
