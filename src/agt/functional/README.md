# Functional Agents

## Overview

This folder contains the functional anomaly detectors of the MAS.

They are organized into two sub-families:
- `apriori`: functional consistency and coverage checks executed before incident-oriented reasoning
- `aposteriori`: functional diagnostic checks executed once incidents, events, or service degradations are already present

Like the structural and dynamic families, the functional agents follow the same implementation pattern:
- one JaCaMo agent per detector
- one Python script per detector
- one SPARQL query per script
- one JSON result file per execution

Results are written under:
- `results/functional/apriori/`
- `results/functional/aposteriori/`

## Scope

The functional family reasons over:
- applications
- services
- application modules
- mappings between applications and resources
- mappings between modules and services
- service hierarchy and service coverage
- service-level incident aggregation and escalation

Its purpose is to diagnose weaknesses and anomalies in the functional layer of the ICT knowledge graph, especially at the interface between business-facing services and technical support chains.

## A Priori Agents

These agents detect functional weaknesses before incident-oriented diagnosis starts.

### `application_without_module_detector`
Detects applications that are not linked to any functional module.

Current SPARQL logic:
- the node is typed as `noria:Application`
- there is no module linked through `noria:applicationModuleOf`

### `application_without_resource_detector`
Detects applications that are not linked to any supporting technical resource.

Current SPARQL logic:
- the node is typed as `noria:Application`
- there is no supporting resource linked through `noria:resourceForApplication`

### `duplicated_functional_mapping_detector`
Detects resources that are mapped to several applications.

Current SPARQL logic:
- resources are grouped through `noria:resourceForApplication`
- the detector returns resources associated with more than one application

### `inconsistent_service_hierarchy_detector`
Detects modules linked to several parent services.

Current SPARQL logic:
- the node is typed as `noria:ApplicationModule`
- parent services are reached through `seas:subSystemOf`
- the detector returns modules having more than one service parent

### `over_concentrated_service_detector`
Detects services whose support is concentrated on too few resources.

Current SPARQL logic:
- services are linked to modules through `seas:subSystemOf`
- modules are linked to applications through `noria:applicationModuleOf`
- applications are linked to resources through `noria:resourceForApplication`
- the detector returns services supported by one resource or fewer

### `service_without_application_detector`
Detects services that are not linked to any application module.

Current SPARQL logic:
- the node is typed as `noria:Service`
- there is no application module linked via `seas:subSystemOf`

### `service_without_resource_coverage_detector`
Detects services whose application chain exposes no visible resource coverage.

Current SPARQL logic:
- the node is typed as `noria:Service`
- there is no full chain:
- service -> module via `seas:subSystemOf`
- module -> application via `noria:applicationModuleOf`
- application -> resource via `noria:resourceForApplication`

## A Posteriori Agents

These agents detect functional anomalies once incidents or events are already present.

### `application_incident_without_resource_detector`
Detects application-level incidents or events whose application has no supporting resource.

Current SPARQL logic:
- starts from `noria:EventRecord`
- links the event to an application through `noria:logOriginatingManagementSystem`
- filters applications with no supporting resource via `noria:resourceForApplication`

### `cascading_service_failure_detector`
Detects patterns where one technical incident may propagate to several services through a shared application and module chain.

Current SPARQL logic:
- starts from `noria:EventRecord`
- reaches the originating resource through `noria:logOriginatingManagedObject`
- follows the chain resource -> application -> module -> service
- returns cases where one module is attached to at least two distinct services

### `conflicting_application_state_detector`
Detects applications associated with several event types at the same timestamp.

Current SPARQL logic:
- starts from `noria:EventRecord`
- groups by application and logging time
- counts distinct `dcterms:type` values
- returns groups with more than one distinct type

### `hidden_service_dependency_detector`
Detects implicit or hidden dependencies between services through a shared support chain.

Current SPARQL logic:
- starts from `noria:EventRecord`
- follows resource -> application -> module -> service
- returns pairs of distinct services attached to the same module
- excludes explicit hierarchy relations between those services

### `module_level_incident_aggregation_detector`
Detects repeated incidents converging on the same application module.

Current SPARQL logic:
- starts from `noria:EventRecord`
- follows resource -> application -> module
- groups by application and module
- returns module chains with more than one distinct event

### `resource_event_without_service_impact_detector`
Detects resource events that cannot be propagated to any service.

Current SPARQL logic:
- starts from `noria:EventRecord`
- reaches the originating resource through `noria:logOriginatingManagedObject`
- filters resources for which no resource -> application -> module -> service chain exists

### `service_impacted_by_multiple_resources_detector`
Detects services impacted by more than one distinct resource.

Current SPARQL logic:
- starts from `noria:EventRecord`
- follows resource -> application -> module -> service
- groups by service
- returns services linked to more than one distinct resource through the event chain

### `service_without_ticket_escalation_detector`
Detects services impacted by events but without any related trouble ticket on the supporting resources.

Current SPARQL logic:
- starts from `noria:EventRecord`
- follows resource -> application -> module -> service
- filters cases with no `noria:TroubleTicket` linked to the supporting resource

### `service_with_repeated_incident_detector`
Detects services repeatedly impacted by events.

Current SPARQL logic:
- starts from `noria:EventRecord`
- follows resource -> application -> module -> service
- groups by service
- returns services associated with more than one distinct event

## Execution Model

Each functional detector:
- is activated only when its family matches the mode selected in `mas.properties`
- focuses on the shared `pyexec` artifact
- launches its Python script through the Java artifact
- executes one SPARQL query against the Virtuoso endpoint
- writes one JSON result file under `results/functional/.../`

## Notes

- The functional family is now implemented on disk with both `apriori` and `aposteriori` detectors.
- As with the other families, effective runtime behavior still depends on ontology alignment, dataset content, and MAS integration in `multiagentSystem.jcm`.
