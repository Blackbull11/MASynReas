# DS27 Scalability Large

## Purpose

This scenario is the large clean graph used as the third point of the scalability curve.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- both

## Mutation Profile

- Start from the quiescent healthy slice of Base B.
- Append two additional healthy service/application/resource stacks.
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
- scalability_curve_point_3

## Expected Level 1 Signals

- no level-1 agent should return any binding

## Expected Level 2 Diagnoses

- no level-2 diagnoser should emit a diagnosis

## Notes

- This is the largest clean runtime baseline in the catalogue.
- It stays semantically healthy while increasing graph size.
