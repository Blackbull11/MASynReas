# DS01 Clean Base A

## Purpose

This scenario is the clean benchmark control of the catalogue. It keeps the healthy structural, functional, and procedural backbone of Base A and removes the live incident layer so the MAS can be evaluated against a strict false-positive baseline.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- both

## Mutation Profile

- Use the quiescent healthy slice of Base A.
- Keep the full support and topology structure intact.
- Keep change requests well formed.
- Remove all 
oria:EventRecord and 
oria:TroubleTicket instances.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- false_positive_control
- activation_correctness
- baseline_runtime
- traceability_sanity_check

## Expected Level 1 Signals

- no level-1 agent should return any binding

## Expected Level 2 Diagnoses

- no level-2 diagnoser should emit a diagnosis

## Notes

- This is the strongest clean control currently available for the MAS.
- It is intentionally quieter than raw Base A to avoid benign aposteriori activations.
