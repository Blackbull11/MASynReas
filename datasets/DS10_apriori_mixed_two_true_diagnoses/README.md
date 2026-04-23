# DS10 Apriori Mixed Two True Diagnoses

## Purpose

This scenario is the first mixed apriori benchmark. One part of the graph should trigger critical service exposure and another should trigger functional mapping gap.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- apriori

## Mutation Profile

- Reduce the customer portal support chain to one resource.
- Remove the monitoring dashboard module to break the monitoring service functional chain.

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
- family_contribution_analysis

## Expected Level 1 Signals

- apriori/structural/criticality_structural_weakness_detector
- apriori/structural/missing_redundancy_detector
- apriori/functional/application_without_module_detector
- apriori/functional/over_concentrated_service_detector
- apriori/functional/service_without_application_detector
- apriori/functional/service_without_resource_coverage_detector

## Expected Level 2 Diagnoses

- apriori/critical_service_exposure_diagnoser
- apriori/functional_mapping_gap_diagnoser

## Notes

- The two target diagnoses are intentionally independent.
- This is a useful early ranking scenario for the apriori layer.
