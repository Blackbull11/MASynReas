# Base A

## Role In The Catalogue

`Base A` is the compact healthy reference graph of the dataset catalogue. It is
the starting point for the clean control case and for the first mutation-driven
scenarios used to validate the MAS on small, readable graphs.

It is intentionally modest in size so that:
- the structure can be inspected manually
- anomalies derived from it remain easy to explain
- false positives are easier to diagnose during early experimentation

## Why This Base Matters

`Base A` gives the benchmark a stable and coherent baseline. Instead of
building every toy dataset from scratch, we mutate a healthy graph whose
topology, support chains, events, tickets, and procedures are already
well-formed. That makes scenario design more rigorous and keeps the expected
diagnoses traceable.

## Design Intent

This reference graph is healthy by construction:
- every resource has visible network interfaces
- applications are supported by modules and resources
- services remain connected to resources through consistent support chains
- events, tickets, and change requests are present and structurally complete
- no obvious anomaly pattern is intentionally embedded in the graph

In practice, this means `Base A` is suitable for:
- clean control runs
- partial-evidence scenarios
- first integrated apriori and aposteriori mutations

## Contents

`baseA.ttl` contains a small but complete ICT slice:
- 2 services
- 2 application modules
- 2 applications
- 6 resources
- 8 interfaces
- 4 network links
- 2 procedures
- 2 changes
- 2 events
- 2 trouble tickets

## Visual Overview

- [baseA.ttl](C:/Users/rdesb/psc/MASynReas/datasets/baseA/baseA.ttl)
- [baseA.png](C:/Users/rdesb/psc/MASynReas/datasets/baseA/baseA.png)

![Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/baseA.png)

## Typical Uses

`Base A` is the source graph for:
- [DS01_clean_baseA](C:/Users/rdesb/psc/MASynReas/datasets/DS01_clean_baseA/README.md)
- partial-evidence scenarios derived from a healthy state
- first compact anomaly scenarios where one mutation should remain easy to
  interpret

## Documentation Note

This README is maintained as UTF-8 without BOM, like the rest of the dataset
documentation, to avoid the encoding issues seen in earlier generated files.
