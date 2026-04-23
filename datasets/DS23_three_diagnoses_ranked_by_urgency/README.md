# DS23 Three Diagnoses Ranked By Urgency

## Purpose

This scenario combines a single point of failure, an unstable component, and a traceability breakdown. It is intended to evaluate ranking quality and priority calibration.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Combine the DS11 single-point-of-failure mutation set.
- Combine the DS15 unstable-component mutation set.
- Break one additional billing ticket-event traceability link.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- top1_diagnosis_accuracy
- mrr
- priority_score_calibration

## Expected Level 1 Signals

- aposteriori/structural/high_impact_resource_detector
- aposteriori/structural/incident_on_incomplete_link_detector
- aposteriori/structural/isolated_incident_resource_detector
- aposteriori/structural/no_redundancy_incident_detector
- aposteriori/dynamic/event_burst_detector
- aposteriori/dynamic/flapping_state_detector
- aposteriori/dynamic/reopened_incident_detector
- aposteriori/procedural/incident_without_ticket_detector
- aposteriori/procedural/ticket_without_linked_event_detector

## Expected Level 2 Diagnoses

- aposteriori/single_point_of_failure_diagnoser
- aposteriori/traceability_breakdown_diagnoser
- aposteriori/unstable_component_diagnoser

## Ranking Expectation

- aposteriori/single_point_of_failure_diagnoser
- aposteriori/unstable_component_diagnoser
- aposteriori/traceability_breakdown_diagnoser

## Notes

- This is the main ranking benchmark for the current catalogue.
- The single point of failure is intended to dominate urgency.
