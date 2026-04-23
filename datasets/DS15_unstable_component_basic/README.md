# DS15 Unstable Component Basic

## Purpose

This scenario creates a classic unstable-component pattern with bursts of follow-up events, contradictory states, and recurrent ticketing on the same anchor.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Add several close-in-time monitoring events on aseB:res_monitor_vm_01.
- Add one resolved ticket followed by a new open ticket on the same element.
- Keep timestamps old enough to satisfy the stale-incident heuristic.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- precision_at_l2
- recall_at_l2
- priority_score_calibration

## Expected Level 1 Signals

- aposteriori/dynamic/event_burst_detector
- aposteriori/dynamic/flapping_state_detector
- aposteriori/dynamic/reopened_incident_detector
- aposteriori/dynamic/repeated_similar_event_detector
- aposteriori/dynamic/stale_incident_detector

## Expected Level 2 Diagnoses

- aposteriori/unstable_component_diagnoser

## Notes

- The target anchor is aseB:res_monitor_vm_01.
- This scenario is useful for validating temporal instability aggregation.
