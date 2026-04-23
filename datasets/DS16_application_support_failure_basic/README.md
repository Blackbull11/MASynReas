# DS16 Application Support Failure Basic

## Purpose

This scenario removes the visible support resources of one application while keeping its incident chain. The resulting ambiguity should support the application-support-failure diagnosis.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Remove both support relations from the billing application nodes.
- Keep the billing event and ticket chain intact.

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

- aposteriori/structural/application_mapping_inconsistency_detector
- aposteriori/functional/application_incident_without_resource_detector

## Expected Level 2 Diagnoses

- aposteriori/application_support_failure_diagnoser

## Notes

- The billing application remains incidented but unsupported in the visible graph.
- This should activate both structural and functional aposteriori families.
