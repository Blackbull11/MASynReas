# Relevant KPI Profile

## Why this profile exists

`KPISGUIDELINE.md` is intentionally broad. The current project, however, uses:
- deterministic Level-1 detectors,
- deterministic Level-2 diagnosers,
- a scenario-based dataset catalogue,
- and benchmark runs centered on one dataset at a time.

So the most useful metrics right now are not necessarily the most classical
ones.

## Primary KPI metrics for the current catalogue

### Level 2 diagnosis quality

- `Activation Correctness`
  because Level-2 activation logic is explicit and central to the MAS design
- `Precision@L2`
  because we want to know whether emitted diagnoses are correct
- `Top-1 Diagnosis Accuracy`
  because the first diagnosis is often the one an operator will inspect first
- `Diagnosis Ranking Quality (MRR)`
  because some scenarios now contain several candidate or true diagnoses

### Time complexity

- `End-to-End Runtime`
- `Mean Runtime per Detector`
- `Mean Runtime per Diagnoser`
- `Controller Waiting Overhead`

These are all directly relevant to the current orchestration architecture.

### Explainability

- `Traceability Rate`
- `Evidence Completeness Ratio`
- `Mean Evidence Count per Diagnosis`
- `Structured Evidence Ratio`

These are directly compatible with the current Level-2 diagnosis JSON schema.

## Scenario-oriented helper metrics

These are not exact copies of the guideline, but they are better suited to the
current catalogue:

- `Diagnosis Hit`
  binary success on datasets where one or a few diagnoses are expected
- `Diagnoser Frequency Rate`
  proportion of applicable scenarios where a diagnoser is successfully matched
- `Clean Control Success`
  success rate on control datasets where no diagnosis should be emitted
- `L1 Expectation Match Rate`
  scenario-level proxy for detector correctness in integrated runs

## Metrics intentionally deferred

### `Recall@L2`

It is mathematically valid, but it is not the best first headline metric for
the current scenario catalogue. In practice, the campaign is easier to read in
terms of:
- diagnosis hit rate,
- diagnoser frequency rate,
- and missed expected diagnoses listed explicitly in each run report.

### `F1@L2`

Deferred for the same reason: it becomes more informative once recall is a
primary campaign metric.

### `Rule Conformance`

Still relevant in principle, but it should be measured on a dedicated detector
micro-suite rather than on the integrated scenario catalogue alone.

### `SPARQL Efficiency`

Relevant architecturally, but not yet instrumented at per-query granularity.

### `Reliability` and `Priority` calibration

Relevant later, once enough scored diagnoses have been collected across many
scenario runs.

### `Robustness` and `Family Contribution`

Relevant as campaign-level studies, not as single-run KPI bundles.
