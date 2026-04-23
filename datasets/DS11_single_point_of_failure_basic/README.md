# DS11 Single Point Of Failure Basic

## Purpose

This scenario concentrates several structural aposteriori clues on one infrastructure element so the MAS can recognize a single point of failure.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Reduce aseB:res_firewall_01 to a single incomplete visible link.
- Add dependent child resources under aseB:res_firewall_01 to make it high impact.
- Add one high-severity open ticket directly impacting aseB:res_firewall_01.

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

- aposteriori/structural/high_impact_resource_detector
- aposteriori/structural/incident_on_incomplete_link_detector
- aposteriori/structural/isolated_incident_resource_detector
- aposteriori/structural/no_redundancy_incident_detector

## Expected Level 2 Diagnoses

- aposteriori/single_point_of_failure_diagnoser

## Notes

- The target anchor is aseB:res_firewall_01.
- This scenario is designed to support a single dominant level-2 diagnosis.
