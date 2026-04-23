# Base B

## Role In The Catalogue

`Base B` is the richer healthy reference graph of the dataset catalogue. It is
used when the benchmark needs denser topology, more operational artefacts, and
enough structure to support ranking, robustness, and scalability studies.

Where `Base A` is meant for compact inspection, `Base B` is meant for more
realistic integrated experiments.

## Why This Base Matters

Many of the later scenarios in the catalogue depend on:
- multiple services and applications
- denser resource support chains
- enough events, tickets, and changes to create competing or interacting
  diagnoses

`Base B` provides that richer healthy baseline without hard-coding anomalies
into the graph itself. This lets us inject faults or remove information in a
controlled way and measure how the MAS reacts.

## Design Intent

`Base B` remains healthy by construction:
- service, module, application, and resource chains are complete
- applications and services have redundant support paths
- resource connectivity is modeled explicitly through interfaces and links
- operational artefacts are present and well formed
- change windows are coherent and non-overlapping in the healthy baseline

It is therefore the preferred source graph for:
- integrated multi-family scenarios
- ranking and calibration cases
- robustness studies
- the three scalability datasets

## Contents

`baseB.ttl` contains a denser benchmark slice:
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

## Visual Overview

- [baseB.ttl](C:/Users/rdesb/psc/MASynReas/datasets/baseB/baseB.ttl)
- [baseB.png](C:/Users/rdesb/psc/MASynReas/datasets/baseB/baseB.png)

![Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/baseB.png)

## Typical Uses

`Base B` is the source graph for:
- integrated diagnosis scenarios from [DS11](C:/Users/rdesb/psc/MASynReas/datasets/DS11_single_point_of_failure_basic/README.md) onward
- ranking and calibration cases such as [DS23](C:/Users/rdesb/psc/MASynReas/datasets/DS23_three_diagnoses_ranked_by_urgency/README.md) and [DS24](C:/Users/rdesb/psc/MASynReas/datasets/DS24_reliability_calibration_bundle/README.md)
- scalability scenarios [DS25](C:/Users/rdesb/psc/MASynReas/datasets/DS25_scalability_small/README.md), [DS26](C:/Users/rdesb/psc/MASynReas/datasets/DS26_scalability_medium/README.md), and [DS27](C:/Users/rdesb/psc/MASynReas/datasets/DS27_scalability_large/README.md)

## Documentation Note

This README is maintained as UTF-8 without BOM, like the rest of the dataset
documentation, to avoid the encoding issues seen in earlier generated files.
