# DS21 Noisy Irrelevant Events

## Purpose

This robustness scenario adds extra benign operational events on a resource outside the service support chains. The expected outcome is weak local noise, not a meaningful diagnosis.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)

Mode:
- aposteriori

## Mutation Profile

- Use the quiescent healthy slice of Base B.
- Add three benign events on aseB:res_firewall_02.
- Keep the events far enough apart to avoid burst-style interpretations.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- noise_robustness
- ranking_stability
- sparql_efficiency_under_noise

## Expected Level 1 Signals

- aposteriori/functional/resource_event_without_service_impact_detector

## Expected Level 2 Diagnoses

- no level-2 diagnoser should emit a diagnosis

## Notes

- The expected output is a weak functional aposteriori signal only.
- No level-2 diagnosis should be emitted.
