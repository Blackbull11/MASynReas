# DS25_scalability_small

## Purpose

Small clean graph for the first point of the scalability curve. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `both`
- Mutation type: `scalability_small`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- No entity removal in this scenario.

### Removed Relations
- No relation removal in this scenario.

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `0`
- Expected Level-2 diagnoses: `0`

### Expected Level-1 Agents
- No Level-1 agent should return a non-zero result.

### Expected Level-2 Diagnosers
- No Level-2 diagnoser should emit a diagnosis.

## KPI Objectives

- Primary focus: `end_to_end_runtime`.
- Primary focus: `mean_runtime_l1` and detector-level runtime breakdowns.
- Primary focus: `mean_runtime_l2` and diagnoser-level runtime breakdowns.
- Reference target: `sparql_efficiency`.
- Scalability focus: first datapoint of the runtime curve.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS25_scalability_small/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS25_scalability_small/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS25_scalability_small/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS25_scalability_small/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
