# DS06 Critical Service Exposure Concentrated Service

## Purpose

This scenario is a stronger version of DS05. The same critical application is left with a single support resource and that remaining support resource is itself structurally weakened.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- apriori

## Mutation Profile

- Reuse the single-support mutation of DS05.
- Remove the explicit interface of aseA:res_customer_vm_01.
- Remove its management assignment.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- severity_score_comparison
- priority_score_comparison

## Expected Level 1 Signals

- apriori/structural/criticality_structural_weakness_detector
- apriori/structural/missing_interface_detector
- apriori/structural/missing_redundancy_detector
- apriori/structural/unmanaged_resource_detector
- apriori/functional/over_concentrated_service_detector

## Expected Level 2 Diagnoses

- apriori/critical_service_exposure_diagnoser

## Notes

- The expected level-2 diagnosis remains critical service exposure.
- Its severity should be higher than in DS05 because the remaining support is also fragile.
