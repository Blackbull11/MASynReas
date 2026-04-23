# DS17 Local Infrastructure Cluster Basic

## Purpose

This scenario creates a local infrastructure cluster by adding several synchronous incident chains on elements co-located in the same room.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Reuse the existing customer warning event in room DC1.
- Add billing and access-switch incident chains in the same room within the same short time window.

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

## Expected Level 1 Signals

- aposteriori/structural/spatial_incident_cluster_detector
- aposteriori/dynamic/multi_element_synchronous_incident_detector

## Expected Level 2 Diagnoses

- aposteriori/local_infrastructure_cluster_diagnoser

## Notes

- The main target is the location cluster in room DC1.
- This scenario is useful for validating localization-aware diagnosis.
