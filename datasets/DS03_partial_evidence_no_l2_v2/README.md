# DS03 Partial Evidence No L2 V2

## Purpose

This scenario extends the partial-evidence family with several weak signals on distinct anchors. It checks that the MAS does not overdiagnose when evidence remains fragmented.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- both

## Mutation Profile

- Remove the management link of one switch resource.
- Remove the actual end time of a different change request.
- Add one event record without timestamp.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- activation_correctness
- false_positive_resistance_under_multi_signal_conditions

## Expected Level 1 Signals

- apriori/structural/unmanaged_resource_detector
- apriori/dynamic/change_without_effective_time_detector
- apriori/dynamic/event_without_timestamp_detector

## Expected Level 2 Diagnoses

- no level-2 diagnoser should emit a diagnosis

## Notes

- Signals are intentionally distributed across unrelated anchors.
- No level-2 diagnoser should aggregate them into a diagnosis.
