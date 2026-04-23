# DS25 Scalability Small

## Purpose

This scenario is the small clean graph used as the first point of the scalability curve.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- both

## Mutation Profile

- Reuse the quiescent healthy slice of Base A.
- Do not inject any anomaly.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- end_to_end_runtime
- mean_runtime_per_detector
- mean_runtime_per_diagnoser
- sparql_efficiency
- scalability_curve_point_1

## Expected Level 1 Signals

- no level-1 agent should return any binding

## Expected Level 2 Diagnoses

- no level-2 diagnoser should emit a diagnosis

## Notes

- This scenario should stay silent at both level 1 and level 2.
- It is the smallest runtime baseline in the catalogue.
