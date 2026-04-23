# DS12 Change Induced Incident Basic

## Purpose

This scenario creates a clear post-change anomaly pattern: overlapping changes on one application are followed by a critical event and an escalated ticket on that same application.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Add an overlapping hotfix change on aseB:app_customer_portal.
- Add a critical event shortly after the end of the release change.
- Add an open high-priority ticket triggered by that event.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- precision_at_l2
- recall_at_l2
- top1_diagnosis_accuracy

## Expected Level 1 Signals

- aposteriori/dynamic/change_followed_by_incident_detector
- aposteriori/dynamic/change_overlap_conflict
- aposteriori/dynamic/critical_event_ticket_escalation_detector

## Expected Level 2 Diagnoses

- aposteriori/change_induced_incident_diagnoser

## Notes

- The target diagnosis is change-induced incident.
- This scenario is suitable for validating temporal explanation chains.
