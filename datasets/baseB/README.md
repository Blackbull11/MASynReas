# Base B

## Purpose

`Base B` is the richer healthy reference graph for `MASynReas`.

It complements `Base A` by providing a larger and more varied operational
baseline for:
- integrated scenarios with several families involved
- ranking and calibration scenarios
- runtime and SPARQL-efficiency measurements
- robustness and scalability experiments

## Design Principles

This graph remains healthy by construction:
- one complete service -> module -> application -> resource chain per business capability
- at least two supporting resources per application and per service
- complete interface and link modeling for every resource
- one well-formed event / ticket chain per impacted service
- one well-formed procedure per event family
- several well-formed change requests on unrelated elements and non-overlapping windows

At the same time, `Base B` is intentionally denser than `Base A` so that
future scenarios can be obtained by local mutation instead of rebuilding the
graph structure from scratch.

## Contents

`baseB.ttl` contains:
- 4 services
- 4 application modules
- 4 applications
- 12 resources
- 16 interfaces
- 8 network links
- 4 procedures
- 3 changes
- 4 events
- 4 trouble tickets

## Intended Use

This graph is the base for:
- mixed integrated scenarios
- ranking and calibration scenarios
- robustness scenarios
- scalability scenarios `DS25`, `DS26`, and `DS27`
