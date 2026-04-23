# DS01 Clean Base A

## Purpose

`DS01_clean_baseA` is the first materialized benchmark scenario of the dataset
catalogue.

It is the clean control scenario used to evaluate:
- false positive control
- activation correctness
- baseline runtime
- traceability sanity

## Relation to Base A

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

It keeps the healthy structural, functional, and procedural backbone of
`Base A`, while using a quiescent operational slice:
- no `noria:EventRecord`
- no `noria:TroubleTicket`

This modeling choice is intentional.

With the current level-1 catalogue, a few `aposteriori` heuristics are
incident-centered enough that even benign warning tickets can create non-zero
outputs in a supposedly clean control graph. For `DS01`, the goal is a strict
false-positive baseline, so the incident layer is removed entirely.

## Contents

Files:
- `dataset.ttl`: the scenario graph
- `manifest.json`: scenario metadata
- `expected_level1.json`: expected level-1 outputs
- `expected_level2.json`: expected level-2 outputs

## Expected Behavior

### In `apriori` mode

The graph should remain healthy:
- no level-1 anomaly detector should return any binding
- no level-2 diagnoser should activate

### In `aposteriori` mode

The graph contains no incident/event/ticket chain:
- `aposteriori` level-1 detectors should return no result
- `aposteriori` level-2 diagnosers should not produce any diagnosis

## Notes

- This scenario is intended for benchmark control, not for detector stress.
- It is a better clean reference than raw `Base A` for the current MAS
  implementation because it neutralizes avoidable heuristic activations in the
  `aposteriori` families.
