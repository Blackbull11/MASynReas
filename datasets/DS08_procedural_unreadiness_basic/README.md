# DS08 Procedural Unreadiness Basic

## Purpose

This scenario combines missing scheduled change metadata, a ticket without assigned procedure, and unused procedures. Together these signals should activate the procedural unreadiness diagnoser.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- apriori

## Mutation Profile

- Remove both scheduled time fields from aseA:change_switch_firmware_window.
- Add one event linked to a new ticket but without proposed repair action.
- Keep the existing procedures unused from the event perspective.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- precision_at_l2
- recall_at_l2
- family_contribution_analysis

## Expected Level 1 Signals

- apriori/procedural/change_request_without_scheduled_time_detector
- apriori/procedural/procedure_not_linked_to_resource_type_detector
- apriori/procedural/ticket_without_assigned_procedure_detector

## Expected Level 2 Diagnoses

- apriori/procedural_unreadiness_diagnoser

## Notes

- This is an apriori scenario with a lightweight ticketing artifact.
- The target diagnosis is procedural unreadiness.
