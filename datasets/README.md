# Dataset Catalogue

## Overview

This folder contains the benchmark catalogue used to evaluate `MASynReas` on
controlled NORIA-O knowledge graphs.

The catalogue is built around a simple idea: start from a small number of
healthy reference graphs, then derive scenario datasets through explicit,
documented mutations. Each scenario is intended to be inspectable by hand,
traceable to a reference graph, and reusable across future MAS runs.

The catalogue therefore supports three complementary needs:
- validating that the MAS remains quiet on clean or weak-evidence cases
- checking whether Level 2 produces the intended diagnoses on integrated cases
- measuring runtime, ranking, traceability, robustness, and scalability on a
  stable experimental base

## Encoding Note

All dataset `README.md` files in this catalogue are maintained as UTF-8 text
without BOM so they render cleanly and avoid the encoding issues that appeared
in earlier generated documentation.

## Catalogue Philosophy

The datasets are not random toy graphs. Each scenario is a compact experiment
with:
- a reference graph of origin
- a mutation profile
- expected Level-1 outputs
- expected Level-2 outputs
- KPI-oriented evaluation goals

This keeps the benchmark reproducible and makes post-run analysis much easier.
When a diagnosis is wrong, we can usually trace the deviation back to a
specific mutation, detector family, or aggregation decision.

## Evaluation Focus

The KPI guideline is intentionally broad, but the current catalogue is best
suited to the metrics that match the present MAS architecture and evaluation
workflow.

### Primary metrics for the current catalogue

- `l2_activation_correctness`
- `precision_l2`
- `top1_accuracy`
- `ranking_mrr`
- `end_to_end_runtime`
- `mean_runtime_l1`
- `mean_runtime_l2`
- `controller_waiting_overhead`
- `traceability_rate`
- `evidence_completeness_ratio`
- `mean_evidence_count`
- `structured_evidence_ratio`

### Scenario-oriented helper metrics

- `diagnosis_hit`
- `clean_control_success`
- `l1_expectation_match_rate`
- diagnoser success frequency across a campaign

### Metrics tracked later or mainly at campaign level

- `Recall@L2`
- `F1@L2`
- reliability and priority calibration
- robustness ratios under missing data or noise
- family contribution through ablation
- detailed SPARQL efficiency

These remain meaningful, but they are better assessed after several runs or
with dedicated experiment suites.

## Folder Structure

The catalogue currently contains:
- 2 reference graphs: `baseA`, `baseB`
- 27 scenario folders: `DS01` to `DS27`

Each materialized scenario folder follows the same structure:
- `dataset.ttl`
- `README.md`
- `manifest.json`
- `expected_level1.json`
- `expected_level2.json`

The catalogue can be regenerated with
[generate_catalogue.ps1](C:/Users/rdesb/psc/MASynReas/datasets/generate_catalogue.ps1).

## Reference Graphs

### Base A

`Base A` is the compact healthy reference graph used for:
- clean control runs
- partial-evidence scenarios
- the first integrated mutation scenarios

Files:
- [Base A README](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)
- [baseA.ttl](C:/Users/rdesb/psc/MASynReas/datasets/baseA/baseA.ttl)
- [baseA.png](C:/Users/rdesb/psc/MASynReas/datasets/baseA/baseA.png)

### Base B

`Base B` is the richer healthy reference graph used for:
- complex integrated scenarios
- ranking and calibration cases
- robustness studies
- scalability measurements

Files:
- [Base B README](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)
- [baseB.ttl](C:/Users/rdesb/psc/MASynReas/datasets/baseB/baseB.ttl)
- [baseB.png](C:/Users/rdesb/psc/MASynReas/datasets/baseB/baseB.png)

## Scenario Families

### 1. Control and Activation Scenarios

These scenarios verify that the MAS behaves conservatively when evidence is
absent, weak, or insufficiently convergent.

- `DS01_clean_baseA`
- `DS02_partial_evidence_no_l2_v1`
- `DS03_partial_evidence_no_l2_v2`

Main use:
- clean-control validation
- false-positive resistance
- activation correctness

### 2. Integrated A Priori Diagnosis Scenarios

These scenarios are designed to exercise the deterministic Level-2 diagnosers
that reason about weaknesses and fragilities independently of a live anomaly.

- `DS04_structural_fragility_resource_anchor`
- `DS05_critical_service_exposure_basic`
- `DS06_critical_service_exposure_concentrated_service`
- `DS07_observability_gap_events_and_changes`
- `DS08_procedural_unreadiness_basic`
- `DS09_functional_mapping_gap_application_chain`
- `DS10_apriori_mixed_two_true_diagnoses`

Main use:
- diagnosis correctness
- ranking between several plausible apriori outcomes
- severity and priority comparisons such as `DS05` vs `DS06`

### 3. Integrated A Posteriori Diagnosis Scenarios

These scenarios model concrete operational anomalies and error situations.

- `DS11_single_point_of_failure_basic`
- `DS12_change_induced_incident_basic`
- `DS13_service_cascade_basic`
- `DS14_traceability_breakdown_basic`
- `DS15_unstable_component_basic`
- `DS16_application_support_failure_basic`
- `DS17_local_infrastructure_cluster_basic`
- `DS18_aposteriori_mixed_two_true_diagnoses`

Main use:
- Level-2 diagnosis correctness
- top-1 diagnosis quality
- ranking quality on multi-diagnosis cases

### 4. Robustness Scenarios

These scenarios are meant to compare the MAS against degraded or noisy variants
of otherwise meaningful cases.

- `DS19_missing_data_structural_and_temporal`
- `DS20_missing_procedural_links`
- `DS21_noisy_irrelevant_events`
- `DS22_noisy_duplicate_and_inconsistent_records`

Main use:
- robustness studies
- traceability degradation analysis
- false-positive sensitivity under noise

### 5. Ranking, Calibration, and Scalability Scenarios

These scenarios are intended for richer campaign-level analyses.

- `DS23_three_diagnoses_ranked_by_urgency`
- `DS24_reliability_calibration_bundle`
- `DS25_scalability_small`
- `DS26_scalability_medium`
- `DS27_scalability_large`

Main use:
- ranking quality
- future calibration analysis
- runtime curves as graph size increases

## How To Use The Catalogue

For one benchmark run:
1. Choose the scenario folder.
2. Load `dataset.ttl` into Virtuoso.
3. Set `mode` and `dataset.id` in [mas.properties](C:/Users/rdesb/psc/MASynReas/mas.properties).
4. Run the MAS.
5. Compute the run KPI report with the tools in [evaluation](C:/Users/rdesb/psc/MASynReas/evaluation/README.md).

For a campaign:
1. Repeat the run on several scenario folders.
2. Store each `run_kpi_report.json`.
3. Aggregate them into campaign-level indicators.

## Notes

This catalogue is not a replacement for dedicated detector unit tests. It is an
integrated evaluation asset for the whole MAS, especially Level 2.

If later experiments require stricter Level-1 rule conformance measurement, the
recommended approach is still to maintain a separate micro-suite with positive,
negative, and boundary cases per detector.
