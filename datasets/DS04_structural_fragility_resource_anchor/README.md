# DS04_structural_fragility_resource_anchor

## Purpose

A single resource accumulates structural weakness signals. This scenario is part of the MASynReas benchmark catalogue and is intended to be used as a controlled, reproducible experiment.

## Scenario Profile

- Reference graph: [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- Source variant: `quiescentA`
- Execution mode: `apriori`
- Mutation type: `structural_anchor_fragility`

## Why This Scenario Exists

This scenario provides a documented mutation of a healthy reference graph so that Level-1 signals, Level-2 diagnoses, and benchmark KPIs can be interpreted against a known expected outcome. It is useful both for debugging the MAS and for producing comparable evaluation results across future runs.

## Mutation Summary

### Injected Anomalies
- No anomaly entity is directly injected; the effect comes from structural or relational mutation.

### Removed Entities
- `baseA:if_switch_02_port_01`
- `baseA:if_switch_02_port_02`

### Removed Relations
- `noria:resourceManagedBy on baseA:res_access_switch_02`
- `seas:subSystemOf on baseA:res_access_switch_02`

### Noise Additions
- No noise is intentionally added in this scenario.

## Expected Diagnostic Footprint

- Expected non-zero Level-1 bindings: `3`
- Expected Level-2 diagnoses: `1`

### Expected Level-1 Agents
- `apriori/structural/missing_interface_detector`
- `apriori/structural/missing_parent_resource_detector`
- `apriori/structural/unmanaged_resource_detector`

### Expected Level-2 Diagnosers
- `apriori/structural_fragility_diagnoser`

## KPI Objectives

- Primary focus: `precision_l2`, with diagnosis matching against the expected Level-2 outputs.
- In the current profile, this is mostly followed through `diagnosis_hit` and the list of missed expected diagnoses.
- Reference target: `family_contribution_analysis`.

## Files

- [dataset.ttl](C:/Users/rdesb/psc/MASynReas/datasets/DS04_structural_fragility_resource_anchor/dataset.ttl)
- [manifest.json](C:/Users/rdesb/psc/MASynReas/datasets/DS04_structural_fragility_resource_anchor/manifest.json)
- [expected_level1.json](C:/Users/rdesb/psc/MASynReas/datasets/DS04_structural_fragility_resource_anchor/expected_level1.json)
- [expected_level2.json](C:/Users/rdesb/psc/MASynReas/datasets/DS04_structural_fragility_resource_anchor/expected_level2.json)

## Notes

- The companion JSON files are the authoritative machine-readable reference for automated evaluation scripts.
- This README is intentionally written for human inspection and benchmark orientation.
- The file is stored as UTF-8 without BOM to avoid the encoding artefacts seen in earlier generated documentation.
