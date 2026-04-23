# DS09 Functional Mapping Gap Application Chain

## Purpose

This scenario targets the functional mapping gap diagnoser by breaking the service -> module -> application chain of one business service.

## Relation to the Reference Graphs

This scenario is derived from:
- [Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)

Mode:
- apriori

## Mutation Profile

- Remove aseA:module_customer_portal.
- Leave the application and resource support in place so the break is localized in the functional layer.

## Contents

Files:
- dataset.ttl
- manifest.json
- expected_level1.json
- expected_level2.json

## KPI Targets

- precision_at_l2
- recall_at_l2

## Expected Level 1 Signals

- apriori/functional/application_without_module_detector
- apriori/functional/service_without_application_detector
- apriori/functional/service_without_resource_coverage_detector

## Expected Level 2 Diagnoses

- apriori/functional_mapping_gap_diagnoser

## Notes

- The functional chain should break without altering the technical support graph.
- The expected diagnosis is functional mapping gap.
