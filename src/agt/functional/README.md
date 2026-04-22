# Functional Agents

## Overview

This folder contains the functional anomaly catalogue of the MAS.

Unlike the structural and dynamic families, this functional family should currently be considered as a planned catalogue rather than a validated implemented subsystem.

The filenames already define the intended detector inventory clearly, so this README documents:
- the planned functional scope
- the intended split between `apriori` and `aposteriori`
- the role suggested by each detector name

It does not claim that all of these agents are already integrated, tested, or behaviorally validated in the MAS runtime.

## Scope

The functional family is intended to reason over anomalies affecting:
- applications
- services
- modules
- functional mappings between business and technical layers
- service coverage and service hierarchy
- service-level incident aggregation and escalation

In other words, this family focuses on the consistency and resilience of the functional layer of the ICT knowledge graph.

## A Priori Catalogue

These planned agents are intended to detect functional weaknesses before incident-oriented diagnosis starts.

### `application_without_module_detector`
Planned role:
- detect applications that are not decomposed into any functional module
- highlight incomplete internal functional modeling

### `application_without_resource_detector`
Planned role:
- detect applications that are not linked to any supporting technical resource
- highlight missing application-to-infrastructure grounding

### `duplicated_functional_mapping_detector`
Planned role:
- detect duplicated or redundant functional mappings
- highlight ambiguity or over-modeling between functional and technical layers

### `inconsistent_service_hierarchy_detector`
Planned role:
- detect inconsistencies in service hierarchy relations
- highlight broken parent-child service organization or contradictory service decomposition

### `over_concentrated_service_detector`
Planned role:
- detect services that rely on an excessively concentrated set of applications or resources
- highlight potential functional bottlenecks or resilience weaknesses

### `service_without_application_detector`
Planned role:
- detect services that are not linked to any application
- highlight incomplete functional realization of declared services

Note:
- the detector filenames are now aligned on `service_without_application_detector`

### `service_without_resource_coverage_detector`
Planned role:
- detect services whose supporting applications do not provide sufficient resource coverage
- highlight weak functional-to-technical support chains

## A Posteriori Catalogue

These planned agents are intended to diagnose functional anomalies after incidents, events, or service degradations appear.

### `application_incident_without_resource_detector`
Planned role:
- detect incidents affecting applications for which no supporting resource is visible
- highlight diagnostic blind spots between application symptoms and infrastructure support

### `cascading_service_failure_detector`
Planned role:
- detect failure cascades across services
- highlight propagation of business impact through service dependencies

### `conflicting_application_state_detector`
Planned role:
- detect contradictory functional states associated with the same application
- highlight inconsistent application-level observability or state fusion issues

### `hidden_service_dependency_detector`
Planned role:
- detect incidents suggesting an implicit or missing dependency between services
- highlight service couplings that are not explicitly modeled

### `module_level_incident_aggregation_detector`
Planned role:
- detect clusters of incidents converging at module level
- highlight modules that act as functional concentration points for anomalies

### `resource_event_without_service_impact_detector`
Planned role:
- detect resource-side anomalous events that do not propagate to any declared service impact
- highlight either benign technical noise or missing service-impact modeling

### `service_impacted_by_multiple_resources_detector`
Planned role:
- detect services simultaneously impacted through several underlying resources
- highlight broad technical support failures affecting one business function

### `service_without_ticket_escalation_detector`
Planned role:
- detect service-impact situations that do not lead to corresponding ticket escalation
- highlight escalation gaps in operational workflows

### `service_with_repeated_incident_detector`
Planned role:
- detect recurring incidents affecting the same service
- highlight unstable or chronically fragile service areas

## Intended Execution Logic

Once fully integrated, the functional family is expected to follow the same overall pattern as the other families:
- `apriori` agents run only in `apriori` mode
- `aposteriori` agents run only in `aposteriori` mode
- each detector launches a dedicated Python query script
- results are written into a dedicated `results/functional/.../` directory structure

## Status

Current documentation status:
- the catalogue exists on disk through the file structure
- this README documents the intended detector inventory
- full implementation status, integration status, and validation status still need to be confirmed agent by agent
