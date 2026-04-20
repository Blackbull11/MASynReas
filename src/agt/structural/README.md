# Structural Agents

## Overview

This folder contains the structural anomaly detectors implemented for the MAS.

They are organized into two sub-families:
- `apriori`: structural consistency checks run independently of any incident context
- `aposteriori`: structural diagnostic checks restricted to resources or applications already involved in incidents

At the moment, the structural layer is implemented as a set of deterministic agents:
- one JaCaMo agent per anomaly pattern
- one Python script per detector
- one SPARQL query per script
- one JSON result file per execution

Results are written under:
- `results/structural/apriori/`
- `results/structural/aposteriori/`

## Scope

The structural detectors currently reason over:
- `noria:Resource`
- `noria:Application`
- `noria:NetworkInterface`
- `noria:NetworkLink`
- `noria:TroubleTicket`
- support relations such as `noria:resourceForApplication`
- management relations such as `noria:resourceManagedBy`
- topology relations such as `noria:networkInterfaceOf`, `noria:networkInterfaceConnects`, `noria:networkLinkTerminationResource`
- containment or hierarchy relations such as `seas:subSystemOf` or `noria:partOf`
- spatial relations such as `noria:locatedIn`

## A Priori Agents

These agents detect structural weaknesses without requiring an incident.

### `orphan_resource_detector`
Detects `noria:Resource` instances that are structurally isolated.

Current SPARQL logic:
- no explicit interface linked via `noria:networkInterfaceOf`
- no application support relation via `noria:resourceForApplication`
- no management relation via `noria:resourceManagedBy`
- no parent via `seas:subSystemOf`
- no child via `seas:subSystemOf`

### `missing_interface_detector`
Detects `noria:Resource` instances without any explicit `noria:NetworkInterface`.

Current SPARQL logic:
- the resource is typed as `noria:Resource`
- there is no interface typed as `noria:NetworkInterface` linked through `noria:networkInterfaceOf`

### `orphan_interface_detector`
Detects `noria:NetworkInterface` instances not attached to any resource.

Current SPARQL logic:
- the interface is typed as `noria:NetworkInterface`
- there is no `noria:networkInterfaceOf` relation linking it to a resource

### `unconnected_interface_detector`
Detects interfaces that are attached to a resource but not connected to any network link.

Current SPARQL logic:
- the interface is typed as `noria:NetworkInterface`
- it is linked to a resource through `noria:networkInterfaceOf`
- it has no `noria:networkInterfaceConnects` relation to a link

### `incomplete_network_link_detector`
Detects `noria:NetworkLink` instances with fewer than two termination resources.

Current SPARQL logic:
- the link is typed as `noria:NetworkLink`
- endpoints are collected through `noria:networkLinkTerminationResource`
- links with fewer than two distinct termination resources are returned

### `missing_parent_resource_detector`
Detects resources that appear structurally subordinate but have no parent resource.

Current SPARQL logic:
- the resource is typed as `noria:Resource`
- it has no parent via `seas:subSystemOf`
- and at least one of the following is true:
- it has children via `seas:subSystemOf`
- or it supports an application via `noria:resourceForApplication`
- or it is managed via `noria:resourceManagedBy`
- the current query excludes resources typed as the rack concept hardcoded in the script

### `application_without_support_detector`
Detects applications not linked to any supporting resource.

Current SPARQL logic:
- the node is typed as `noria:Application`
- there is no resource linked to it via `noria:resourceForApplication`

### `unmanaged_resource_detector`
Detects resources with no management assignment.

Current SPARQL logic:
- the node is typed as `noria:Resource`
- there is no `noria:resourceManagedBy` relation

### `missing_redundancy_detector`
Detects critical applications supported by fewer than two distinct resources.

Current SPARQL logic:
- the node is typed as `noria:Application`
- it has a `noria:businessCriticality`
- the accepted criticality values in the current query are `critical` and `high-critical`
- supporting resources are collected through `noria:resourceForApplication`
- applications with fewer than two distinct supporting resources are returned

### `criticality_structural_weakness_detector`
Detects critical applications whose visible technical support appears too weak.

Current SPARQL logic:
- same structural condition as `missing_redundancy_detector`
- the result also keeps the criticality value explicitly in the output

## A Posteriori Agents

These agents detect structural patterns around incident-affected resources or applications.

### `isolated_incident_resource_detector`
Detects incident-related resources with very low visible network connectivity.

Current SPARQL logic:
- starts from `noria:TroubleTicket`
- follows `noria:troubleTicketImpacts` toward a `noria:Resource`
- counts connected `noria:NetworkLink` instances reachable through `noria:networkInterfaceOf` and `noria:networkInterfaceConnects`
- returns resources with a connectivity degree less than or equal to 1

### `incident_on_incomplete_link_detector`
Detects incidents involving resources connected to incomplete links.

Agent/script note:
- the JaCaMo agent is named `incident_on_incomplete_link_detector`
- the current Python script filename is `incident_on_incomple_link_detector.py`

Current SPARQL logic:
- starts from `noria:TroubleTicket`
- follows `noria:troubleTicketImpacts` toward a `noria:Resource`
- retrieves the impacted resource interfaces via `noria:networkInterfaceOf`
- retrieves the connected links via `noria:networkInterfaceConnects`
- counts the distinct interfaces connected to each link
- returns cases where the link has at most one connected interface

### `high_impact_resource_detector`
Detects incident-affected resources with many structural dependents.

Current SPARQL logic:
- starts from `noria:TroubleTicket`
- follows `noria:troubleTicketImpacts` toward a `noria:Resource`
- counts dependent resources through `noria:partOf`
- counts supported applications through `noria:resourceForApplication`
- returns resources whose total dependent-resource count plus dependent-application count is at least 3

### `no_redundancy_incident_detector`
Detects incident-affected resources with no visible structural redundancy.

Agent/script note:
- the JaCaMo agent is named `no_redundancy_incident_detector`
- the current Python script filename is `no_redundancy_detector.py`

Current SPARQL logic:
- starts from `noria:TroubleTicket`
- follows `noria:troubleTicketImpacts` toward a `noria:Resource`
- excludes resources having a sibling resource sharing the same parent via `noria:partOf`
- excludes resources having another resource connected to the same link through interface-link relations
- returns incident-related resources for which neither sibling-based nor link-based redundancy is visible

### `application_mapping_inconsistency_detector`
Detects incidents involving applications whose technical support mapping is missing or structurally fragmented.

Current SPARQL logic:
- starts from `noria:TroubleTicket`
- follows `noria:troubleTicketImpacts` toward a `noria:Application`
- collects support resources via `noria:resourceForApplication`
- optionally groups these support resources by parent through `noria:partOf`
- returns applications with either:
- zero supporting resources
- or more than one support resource distributed across more than one parent support group

### `spatial_incident_cluster_detector`
Detects clusters of incidents concentrated in the same location.

Current SPARQL logic:
- starts from `noria:TroubleTicket`
- follows `noria:troubleTicketImpacts` toward a `noria:Resource`
- uses `noria:locatedIn` to group impacted resources by location
- returns locations associated with at least two distinct trouble tickets

### `child_component_incident_escalation_detector`
Detects incidents affecting child components whose parent resource appears structurally important.

Current SPARQL logic:
- starts from `noria:TroubleTicket`
- follows `noria:troubleTicketImpacts` toward a child `noria:Resource`
- climbs to a parent resource via `noria:partOf`
- counts sibling or child resources linked to the same parent
- counts applications supported by that parent through `noria:resourceForApplication`
- returns parent resources having either at least two contained resources or at least one supported application

## Control Agent

The `apriori` folder also contains:
- `apriori_test_controller`

This is not an anomaly detector. It is a coordination agent used to observe Python execution completion signals and stop the MAS after all a priori detectors have reported.

## Execution Model

Each structural detector:
- is declared as a JaCaMo agent
- focuses on the shared `pyexec` artifact
- launches one Python script
- executes one SPARQL query against the Virtuoso endpoint
- writes one JSON result file in the appropriate `results/structural/.../` directory

## Notes

- This README documents the effective code currently present in `src/agt/structural`.
- It intentionally avoids documenting structural agents that are not implemented yet.
- Some detectors are heuristic by design because the toy dataset does not expose every NORIA-O relation with the same level of detail.
