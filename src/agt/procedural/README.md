# Procedural Agents

## Overview

This folder contains the procedural anomaly detectors of the MAS.

They are organized into two sub-families:
- `apriori`: procedural preparedness and process-completeness checks executed before incident-oriented diagnosis
- `aposteriori`: procedural consistency and traceability checks executed once changes, tickets, or incidents are already present

Like the other families, the procedural agents follow the same implementation pattern:
- one JaCaMo agent per detector
- one Python script per detector
- one SPARQL query per script
- one JSON result file per execution

Results are written under:
- `results/procedural/apriori/`
- `results/procedural/aposteriori/`

## Scope

The procedural family reasons over:
- `noria:ChangeRequest`
- `noria:TroubleTicket`
- `noria:EventRecord`
- `pep:Procedure`
- links between operational procedures, tickets, changes, and events
- procedural preparedness, ticket/procedure association, and change/ticket traceability

Its purpose is to diagnose weaknesses and anomalies in the operational process layer of the ICT knowledge graph.

## A Priori Agents

These agents detect missing procedural preparation before incident-oriented diagnosis starts.

### `change_request_without_scheduled_time_detector`
Detects change requests without scheduled execution time information.

Current SPARQL logic:
- the node is typed as `noria:ChangeRequest`
- `noria:changeStatus` is optional
- the detector returns changes that have none of:
- `noria:plannedStartDate`
- `noria:plannedEndDate`
- `noria:changeDate`

### `procedure_not_linked_to_resource_type_detector`
Detects procedures that are not linked to any resource type through observed event usage.

Current SPARQL logic:
- the node is typed as `pep:Procedure`
- the detector excludes procedures for which there exists:
- an `noria:EventRecord`
- recommending that procedure via `noria:alarmProposedRepairAction`
- on a `noria:Resource` carrying `noria:resourceType`

### `ticket_without_assigned_procedure_detector`
Detects trouble tickets that cannot be associated with any procedure through linked events.

Current SPARQL logic:
- the node is typed as `noria:TroubleTicket`
- ticket status, priority, and severity are optional
- the detector returns tickets for which no linked event proposes a procedure
- event links are checked through:
- `noria:troubleTicketTrigger`
- or `dcterms:relation`

## A Posteriori Agents

These agents detect procedural anomalies once operational artifacts such as changes, tickets, and incidents already exist.

### `change_linked_to_multiple_incidents_detector`
Detects change requests linked to several trouble tickets.

Current SPARQL logic:
- starts from `noria:ChangeRequest` and `noria:TroubleTicket`
- links are checked bidirectionally through `dcterms:relation`
- the detector returns changes linked to more than one distinct ticket

### `incident_without_ticket_detector`
Detects incident-like events that are not linked to any trouble ticket.

Current SPARQL logic:
- starts from `noria:EventRecord`
- severity is required through `noria:alarmSeverity`
- time and related element are optional
- the detector excludes events linked to a ticket through:
- `dcterms:relation`
- or `noria:documentStatusHistory`

### `ticket_without_linked_event_detector`
Detects trouble tickets that are not linked to any event record.

Current SPARQL logic:
- starts from `noria:TroubleTicket`
- status and creation date are optional
- the detector excludes tickets linked to an event through:
- `dcterms:relation`
- or `noria:documentStatusHistory`

## Execution Model

Each procedural detector:
- is activated only when its family matches the mode selected in `mas.properties`
- focuses on the shared `pyexec` artifact
- launches its Python script through the Java artifact
- executes one SPARQL query against the Virtuoso endpoint
- writes one JSON result file under `results/procedural/.../`

## Notes

- The procedural family is now implemented on disk with both `apriori` and `aposteriori` detectors.
- Effective runtime behavior still depends on ontology alignment, dataset content, and MAS integration in `multiagentSystem.jcm`.
