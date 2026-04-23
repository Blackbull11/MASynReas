# KPI Evaluation

## Purpose

This folder prepares `MASynReas` for KPI assessment during future runs of the
MAS on the dataset catalogue.

The goal is not to claim that every KPI from `KPISGUIDELINE.md` is equally
relevant right now. Instead, this folder selects the metrics that fit:
- the current deterministic architecture of the MAS,
- the current dataset catalogue,
- and the intended evaluation workflow based on repeated scenario runs.

## Selected KPI Strategy

### Primary metrics prepared now

These metrics are implemented or instrumented for future runs:
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

### Helper metrics prepared now

These helper metrics are not direct copies of the KPI guideline, but they are
useful for the current benchmark design:
- `l1_expectation_match_rate`
- `diagnosis_hit`
- `clean_control_success`
- diagnoser-level frequency rates in campaign aggregation

These helpers are especially useful because the current catalogue is organized
as scenario runs, often with one main intended diagnosis per dataset.

## Metrics considered secondary or deferred

The following KPIs from the guideline are intentionally not treated as primary
single-run metrics at this stage:
- `Rule Conformance`
  because it needs dedicated micro-fixtures per detector, not only integrated
  dataset scenarios
- `Recall@L2`
  because the current campaign is better interpreted through diagnosis hit rate
  and diagnoser frequency across scenarios
- `F1@L2`
  because it depends on recall and is not the most informative first summary
  for the current scenario-oriented benchmark
- `SPARQL Efficiency`
  because the current implementation does not yet instrument per-query latency
  inside every detector script
- `Reliability-Score Calibration`
  and `Priority-Score Calibration`
  because they become meaningful only once enough scored diagnoses have been
  accumulated across many runs
- `Robustness to Missing Data`, `Noise Robustness`, and `Family Contribution`
  because they require campaign-level comparisons or ablations, not one
  isolated run

## Runtime Instrumentation

`PythonExecArtifact.java` now writes runtime metadata under:
- `results/metrics/run_context.json`
- `results/metrics/runtime_events.jsonl`

This enables later computation of:
- per-script runtime
- mean runtime at Level 1 and Level 2
- end-to-end runtime
- controller waiting overhead

To make reports attributable, set the dataset identifier in:
- [mas.properties](C:/Users/rdesb/psc/MASynReas/mas.properties)

Expected property:
- `dataset.id=DS01_clean_baseA`

## Scripts

### `compute_run_kpis.py`

Computes the relevant KPI bundle for one run of the MAS against one dataset.

Typical usage:

```powershell
python evaluation/compute_run_kpis.py --dataset-id DS11_single_point_of_failure_basic --mode aposteriori
```

Default output:
- `results/metrics/run_kpi_report.json`

### `aggregate_kpis.py`

Aggregates several run reports to produce campaign-level metrics such as:
- diagnosis success rate
- clean control success rate
- top-1 accuracy
- MRR
- diagnoser frequency rate
- mean runtime summaries

Typical usage:

```powershell
python evaluation/aggregate_kpis.py --reports-dir evaluation/reports
```

## Suggested Evaluation Workflow

1. Set `dataset.id` and `mode` in [mas.properties](C:/Users/rdesb/psc/MASynReas/mas.properties).
2. Load the corresponding dataset into Virtuoso.
3. Run the MAS.
4. Run `compute_run_kpis.py`.
5. Store the resulting `run_kpi_report.json` for the campaign.
6. After several runs, call `aggregate_kpis.py`.
