# DS18 Aposteriori Mixed Two True Diagnoses

## Purpose

This scenario mixes a service-cascade pattern with an unstable-component pattern so the level-2 layer must separate two true diagnoses.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Create the shared monitoring/workforce module dependency from DS13.
- Create the unstable monitor component timeline from DS15.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- precision_at_l2
- recall_at_l2
- top1_diagnosis_accuracy
- mrr
- family_contribution_analysis

## Expected Level 1 Signals

- aposteriori/dynamic/event_burst_detector
- aposteriori/dynamic/flapping_state_detector
- aposteriori/dynamic/reopened_incident_detector
- aposteriori/functional/cascading_service_failure_detector
- aposteriori/functional/hidden_service_dependency_detector

## Expected Level 2 Diagnoses

- aposteriori/service_cascade_diagnoser
- aposteriori/unstable_component_diagnoser

## Notes

- The two intended diagnoses should remain distinguishable.
- This is a key mixed scenario for ranking quality.
