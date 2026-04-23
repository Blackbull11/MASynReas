# DS24 Reliability Calibration Bundle

## Purpose

This scenario deliberately mixes a weak observability gap, a medium critical service exposure, and a strong structural fragility case. It is intended for reliability-calibration experiments.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- both

## Mutation Profile

- Add one event without related element and remove one change actual end time.
- Reduce the customer portal support chain to one resource.
- Create a strongly fragile firewall resource by removing its interfaces, parent, and management.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- reliability_score_calibration
- activation_threshold_sanity

## Expected Level 1 Signals

- apriori/structural/criticality_structural_weakness_detector
- apriori/structural/missing_interface_detector
- apriori/structural/missing_parent_resource_detector
- apriori/structural/missing_redundancy_detector
- apriori/structural/unmanaged_resource_detector
- apriori/dynamic/change_without_effective_time_detector
- apriori/dynamic/event_without_related_element_detector
- apriori/functional/over_concentrated_service_detector

## Expected Level 2 Diagnoses

- apriori/critical_service_exposure_diagnoser
- apriori/observability_gap_diagnoser
- apriori/structural_fragility_diagnoser

## Ranking Expectation

- apriori/structural_fragility_diagnoser
- apriori/critical_service_exposure_diagnoser
- apriori/observability_gap_diagnoser

## Notes

- This scenario is not about urgency but about evidence strength.
- The structural fragility case is intended to have the strongest support.
