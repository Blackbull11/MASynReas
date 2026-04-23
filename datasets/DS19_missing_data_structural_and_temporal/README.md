# DS19 Missing Data Structural And Temporal

## Purpose

This robustness scenario removes a few key structural and temporal facts from an otherwise healthy operational graph. The point is to observe graceful degradation rather than a strong diagnosis.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- both

## Mutation Profile

- Remove the timestamp of aseB:event_monitoring_warning.
- Remove the related element of aseB:event_workforce_warning.
- Remove the explicit interface of aseB:res_billing_api_02.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- missing_data_robustness
- activation_correctness

## Expected Level 1 Signals

- apriori/structural/missing_interface_detector
- apriori/dynamic/event_without_related_element_detector
- apriori/dynamic/event_without_timestamp_detector

## Expected Level 2 Diagnoses

- no level-2 diagnoser should emit a diagnosis

## Notes

- This scenario is intended to stay below a strong level-2 diagnosis threshold.
- It is mainly a robustness probe for level-1 behavior.
