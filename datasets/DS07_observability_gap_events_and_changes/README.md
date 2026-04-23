# DS07 Observability Gap Events And Changes

## Purpose

This scenario targets the observability-gap diagnoser by combining incomplete change timing with event records that lack core observability fields.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- apriori

## Mutation Profile

- Remove the actual end time of both change requests.
- Add one event without timestamp.
- Add one event without related element.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- precision_at_l2
- recall_at_l2
- reliability_score_calibration

## Expected Level 1 Signals

- apriori/dynamic/change_without_effective_time_detector
- apriori/dynamic/event_without_related_element_detector
- apriori/dynamic/event_without_timestamp_detector

## Expected Level 2 Diagnoses

- apriori/observability_gap_diagnoser

## Notes

- This scenario concentrates on observability, not on service fragility.
- The expected level-2 outcome is a single observability-gap diagnosis.
