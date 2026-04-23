# DS22 Noisy Duplicate And Inconsistent Records

## Purpose

This scenario introduces weakly inconsistent functional records on a low-stakes shadow chain. The purpose is to test resistance to benign inconsistency without forcing a high-level diagnosis.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- both

## Mutation Profile

- Use the quiescent healthy slice of Base B.
- Add a shadow module attached to two services.
- Add one shadow resource mapped to two applications.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- noise_robustness
- false_positive_sensitivity

## Expected Level 1 Signals

- apriori/functional/duplicated_functional_mapping_detector
- apriori/functional/inconsistent_service_hierarchy_detector

## Expected Level 2 Diagnoses

- no level-2 diagnoser should emit a diagnosis

## Notes

- The expected result is a few level-1 functional warnings only.
- No level-2 diagnoser should activate on this shadow chain.
