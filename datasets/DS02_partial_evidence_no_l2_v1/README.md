# DS02 Partial Evidence No L2 V1

## Purpose

This scenario introduces a very small number of isolated weak signals. It is intended to verify that level 1 can react locally while level 2 remains silent because there is no convergent diagnostic anchor.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- both

## Mutation Profile

- Remove the actual end time of one change request.
- Add one event record without a related element.
- Keep the rest of the graph healthy and incident-free.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- activation_correctness
- false_positive_resistance

## Expected Level 1 Signals

- apriori/dynamic/change_without_effective_time_detector
- apriori/dynamic/event_without_related_element_detector

## Expected Level 2 Diagnoses

- no level-2 diagnoser should emit a diagnosis

## Notes

- Only two level-1 agents should react.
- No level-2 diagnoser should activate.
