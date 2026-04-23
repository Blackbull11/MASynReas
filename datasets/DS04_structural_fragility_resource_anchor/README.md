# DS04 Structural Fragility Resource Anchor

## Purpose

This scenario is the first integrated apriori diagnosis case. A single resource accumulates enough structural weakness indicators to support the structural fragility diagnoser.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- apriori

## Mutation Profile

- Remove the management relation of aseA:res_access_switch_02.
- Remove its structural parent relation.
- Remove its two explicit interfaces.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- precision_at_l2
- recall_at_l2
- family_contribution_analysis

## Expected Level 1 Signals

- apriori/structural/missing_interface_detector
- apriori/structural/missing_parent_resource_detector
- apriori/structural/unmanaged_resource_detector

## Expected Level 2 Diagnoses

- apriori/structural_fragility_diagnoser

## Notes

- The target anchor is the switch resource itself.
- This scenario is intentionally apriori-only.
