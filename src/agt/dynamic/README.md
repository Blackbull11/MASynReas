# Dynamic Agents

## Overview

This folder contains the dynamic anomaly detectors currently implemented in the MAS.

They are organized into two sub-families:
- `apriori`: dynamic observability and temporal-consistency checks that can be run before incident-oriented reasoning
- `aposteriori`: dynamic diagnostic checks that analyze incidents, events, and changes once anomalies are already observed

At this stage, each detector is implemented as:
- one JaCaMo agent
- one Python script
- one SPARQL query
- one JSON result file

Results are written under:
- `results/dynamic/apriori/`
- `results/dynamic/aposteriori/`

## Scope

The dynamic family currently reasons over temporal and event-driven entities such as:
- `noria:EventRecord`
- `noria:ChangeRequest`
- `noria:TroubleTicket`
- temporal attributes such as logging times and actual change times
- event-to-element, change-to-element, and ticket-to-element relations
- temporal succession, recurrence, overlap, propagation, and escalation patterns

## A Priori Agents

These agents detect missing temporal or observability information before deeper dynamic diagnosis is attempted.

### `change_without_effective_time_detector`
Detects `noria:ChangeRequest` instances with incomplete actual execution time information.

Current SPARQL logic:
- the node is typed as `noria:ChangeRequest`
- `noria:changeRequestActualStartTime` is optional
- `noria:changeRequestActualEndTime` is optional
- the detector returns changes missing at least one of these two values

### `event_without_timestamp_detector`
Detects `noria:EventRecord` instances with no logging timestamp.

Current SPARQL logic:
- the node is typed as `noria:EventRecord`
- there is no `noria:loggingTime` value

### `event_without_related_element_detector`
Detects `noria:EventRecord` instances that are not linked to any related element.

Current SPARQL logic:
- the node is typed as `noria:EventRecord`
- there is no `noria:eventRelatedElement` value

## A Posteriori Agents

These agents detect dynamic patterns once incidents, events, or changes are already present in the graph.

### `change_followed_by_incident_detector`
Detects patterns where a change is followed shortly afterwards by an event on the same related element.

### `change_overlap_conflict`
Detects overlapping changes affecting the same related element.

### `critical_event_ticket_escalation_detector`
Detects patterns where a critical-like event is followed by the opening of a high-severity, high-priority, or high-urgency trouble ticket.

### `event_burst_detector`
Detects bursts of events affecting the same related element within a short time window.

### `flapping_state_detector`
Detects rapid alternation of contradictory state-related events, such as `UP`/`DOWN`, on the same related element.

### `incident_propagation_detector`
Detects short-delay propagation patterns where an event on one element is followed by an event on a structurally adjacent element.

### `multi_element_synchronous_incident_detector`
Detects incidents where several distinct related elements are affected within a common short time window.

### `parent_child_event_escalation_detector`
Detects temporally close parent/child event pairs affecting structurally related elements.

### `reopened_incident_detector`
Detects incident recurrence patterns where a recently closed ticket is followed by a new active ticket on the same related element.

### `repeated_similar_event_detector`
Detects repeated similar events affecting the same related element within a short time window.

### `silent_degradation_after_change_detector`
Detects cases where a completed change is followed by a progressive accumulation of weak or non-critical events on the same related element.

### `stale_incident_detector`
Detects persistent incidents where an active ticket remains unresolved while new events continue on the same related element.

## Execution Model

Each dynamic detector:
- is activated only when its family matches the mode selected in `mas.properties`
- focuses on the shared `pyexec` artifact
- launches its Python script through the Java artifact
- executes one SPARQL query against the Virtuoso endpoint
- writes one JSON result file under `results/dynamic/.../`

## Notes

- This README documents the dynamic agents that are currently present in the repository.
- The README follows the effective script behavior, even if some `.asl` comment headers still need cleanup.
- The Python interpreter used by the MAS is configured in `mas.properties` through `python.path`.
