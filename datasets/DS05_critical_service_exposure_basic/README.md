# DS05 Critical Service Exposure Basic

## Purpose

This scenario creates the basic form of critical service exposure by reducing a critical application and its service chain to a single visible support resource.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- apriori

## Mutation Profile

- Remove the application support relation from aseA:res_customer_vm_02 to aseA:app_customer_portal.
- Keep the service and module chain otherwise healthy.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- precision_at_l2
- severity_score_comparison

## Expected Level 1 Signals

- apriori/structural/criticality_structural_weakness_detector
- apriori/structural/missing_redundancy_detector
- apriori/functional/over_concentrated_service_detector

## Expected Level 2 Diagnoses

- apriori/critical_service_exposure_diagnoser

## Notes

- This is the reference case for the critical service exposure severity comparison.
- The diagnosis remains focused on the customer portal support chain.
