# DS13 Service Cascade Basic

## Purpose

This scenario creates a hidden service dependency by attaching the same module to two services. Existing monitoring events should then support a service-cascade diagnosis.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Add a second service parent to aseB:module_monitoring_dashboard.
- Reuse the existing monitoring event chain.

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

- aposteriori/functional/cascading_service_failure_detector
- aposteriori/functional/hidden_service_dependency_detector

## Expected Level 2 Diagnoses

- aposteriori/service_cascade_diagnoser

## Notes

- The scenario intentionally reuses healthy operational data from Base B.
- The diagnosis comes from hidden functional coupling, not from extra noise.
