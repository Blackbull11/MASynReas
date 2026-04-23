# Level 2 - Diagnosis Agents

## Overview

The level-2 layer is the deterministic diagnosis layer of MASynReas.

Unlike level 1, where each agent detects one elementary anomaly pattern through one SPARQL query, a level-2 agent:
- reads several level-1 JSON result files
- checks a conditional activation rule
- correlates evidence on shared anchors
- infers a higher-level diagnosis
- computes a reliability score
- computes a severity score
- derives a priority score
- exports one explicit diagnosis JSON file

The guiding principle is:

`1 diagnosis family = 1 level-2 agent = N level-1 inputs = 1 diagnosis output`

Level 2 is divided only by MAS execution mode:
- `apriori`: diagnosis of weaknesses before incidents
- `aposteriori`: diagnosis of anomaly causes, propagation, and operational failures after incidents

## Architecture

The current level-2 implementation is organized as follows:

- `src/agt/level2/apriori`
  Contains the level-2 agents that diagnose weaknesses before incidents.
- `src/agt/level2/aposteriori`
  Contains the level-2 agents that interpret anomalies after incidents.
- `src/agt/level2/common.py`
  Shared deterministic utilities for loading level-1 outputs, correlating anchors, computing scores, and exporting standardized JSON payloads.
- `src/agt/level2/level2_controller.asl`
  Waits for the selected level-1 catalogue to finish, then launches the matching level-2 catalogue.

Results are written under:
- `results/level2/apriori/`
- `results/level2/aposteriori/`

## Core Concepts

### Anchor

An anchor is the common entity or scope on which several level-1 detections are correlated.

Typical anchors include:
- `Resource`
- `Application`
- `Service`
- `ApplicationModule`
- `ChangeRequest`
- `TroubleTicket`
- `Location`
- `Event`
- `RelatedElement`

A level-2 diagnosis should only be produced when the evidence is coherent enough around one anchor or one operational scope.

### Evidence Roles

Each level-1 agent linked to a diagnosis family is assigned one of three roles:

- `P` = Primary evidence
  Strong direct evidence for the diagnosis family.
- `S` = Supporting evidence
  Reinforces the diagnosis but is not usually sufficient alone.
- `C` = Contextual evidence
  Adds operational context, impact, or prioritization information.

## Scores

### Reliability Score

The reliability score answers:

`How strongly do the available level-1 results support this diagnosis?`

It measures evidential confidence, not operational danger.

According to the guideline, reliability should depend on:
- the number of primary detections
- the number of supporting detections
- cross-family convergence of evidence
- coherence of the anchor
- possible contradictions if they are modeled

Recommended default weighting from the guideline:
- each `P` evidence: `+20`
- each `S` evidence: `+10`
- at least 2 ontology families represented: `+10`
- at least 3 ontology families represented: `+20`
- all evidence aligned on the same anchor: `+15`
- partial anchor coherence only: `+5`
- contradictions: `-10` to `-20`

Recommended formula:

```text
reliability_raw =
  primary_score
+ supporting_score
+ cross_family_bonus
+ anchor_bonus
- contradiction_penalty
```

```text
reliability_score = min(100, max(0, reliability_raw))
```

Interpretation scale:
- `0-39`: weak hypothesis
- `40-59`: plausible hypothesis
- `60-79`: strong hypothesis
- `80-100`: very strong hypothesis

### Severity Score

The severity score answers:

`If this diagnosis is true, how serious is it operationally?`

It is independent from reliability.

A diagnosis may therefore be:
- reliable but not very severe
- severe but only moderately supported

According to the guideline, severity should reflect:
- business criticality
- breadth of impact
- concentration or fragility
- temporal aggravation
- governance or operational control weakness
- an optional diagnosis-family base bonus

Recommended severity dimensions:
- `criticality_component` in `0-20`
- `breadth_component` in `0-15`
- `concentration_component` in `0-20`
- `temporal_component` in `0-20`
- `governance_component` in `0-15`
- `family_base_bonus` in `0-10`

Recommended formula:

```text
severity_raw =
  criticality_component
+ breadth_component
+ concentration_component
+ temporal_component
+ governance_component
+ family_base_bonus
```

```text
severity_score = min(100, max(0, severity_raw))
```

Interpretation scale:
- `0-24`: low
- `25-49`: moderate
- `50-74`: high
- `75-100`: critical

### Priority Score

The priority score is a ranking score derived from reliability and severity.

Its purpose is to answer:

`Which diagnosis should be inspected first?`

It does not replace reliability or severity. It is used for ordering and triage.

Recommended formula from the guideline:

```text
priority_score = round(0.55 * reliability_score + 0.45 * severity_score)
```

Alternative formula if operational danger must dominate:

```text
priority_score = round(0.40 * reliability_score + 0.60 * severity_score)
```

The current shared implementation in `common.py` uses the first formula.

## Activation Logic

Level-2 agents should not run blindly on every execution.

Each level-2 agent is expected to:
- read the relevant level-1 result files
- check whether the minimum evidence combination is present
- export an explicit `not_triggered` result if activation conditions are not met

This avoids:
- weak or artificial correlations
- noisy outputs
- unnecessary level-2 diagnoses when the evidence is too sparse

## Output Format

Each level-2 agent writes a JSON object to `results/level2/<mode>/<agent>.json`.

Typical structure:

```json
{
  "agent": "service_cascade_diagnoser",
  "mode": "aposteriori",
  "activation_status": "triggered",
  "reason": "Activation conditions satisfied around Service 'SVC_TOY_DBAccess'.",
  "diagnoses": [
    {
      "diagnosis_id": "L2-P3-001",
      "diagnosis_type": "service_cascade",
      "mode": "aposteriori",
      "target_type": "Service",
      "target_id": "https://w3id.org/noria/object/SVC_TOY_DBAccess",
      "reliability_score": 81,
      "severity_score": 74,
      "priority_score": 78,
      "evidence": [],
      "severity_factors": {},
      "explanation": "...",
      "recommended_action": "..."
    }
  ]
}
```

If a level-2 agent is not triggered, it still writes an explicit file with:
- `activation_status: "not_triggered"`
- a human-readable `reason`
- an empty `diagnoses` list

## A Priori Diagnosis Agents

### `structural_fragility_diagnoser`

Purpose:
- diagnoses resources or support anchors that accumulate several structural weaknesses before any explicit incident occurs

Intuition:
- some assets are fragile because they combine isolation, missing interfaces, weak topology, weak redundancy, poor parentage, or missing management visibility

Main linked level-1 agents:
- `orphan_resource_detector`
- `missing_interface_detector`
- `orphan_interface_detector`
- `unconnected_interface_detector`
- `incomplete_network_link_detector`
- `missing_parent_resource_detector`
- `application_without_support_detector`
- `unmanaged_resource_detector`
- `missing_redundancy_detector`
- `criticality_structural_weakness_detector`

Typical anchor:
- `Resource`
- `Application`
- `Interface`
- `NetworkLink`

### `critical_service_exposure_diagnoser`

Purpose:
- diagnoses service or application support chains that are business-important but structurally and functionally too weak

Intuition:
- a critical application or service is exposed when technical support is missing, incomplete, over-concentrated, or under-redundant

Main linked level-1 agents:
- `missing_redundancy_detector`
- `criticality_structural_weakness_detector`
- `application_without_resource_detector`
- `service_without_resource_coverage_detector`
- `over_concentrated_service_detector`
- `service_without_application_detector`
- `application_without_support_detector`
- `application_without_module_detector`

Typical anchor:
- `Application`
- `Service`

### `observability_gap_diagnoser`

Purpose:
- diagnoses zones where future incident reconstruction and interpretation will be weakened by missing temporal or referential information

Intuition:
- if events and changes lack timestamps, related elements, or execution timing, later diagnoses will be less reliable

Main linked level-1 agents:
- `event_without_timestamp_detector`
- `event_without_related_element_detector`
- `change_without_effective_time_detector`
- `change_request_without_scheduled_time_detector`

Typical anchor:
- `Event`
- `ChangeRequest`
- `RelatedElement`

### `procedural_unreadiness_diagnoser`

Purpose:
- diagnoses operational zones where incident handling is likely to be delayed or inconsistent because procedures are missing or disconnected

Intuition:
- a technically modeled graph can still be operationally weak if changes are unscheduled, procedures are not linked to resource types, or tickets have no assigned procedure

Main linked level-1 agents:
- `change_request_without_scheduled_time_detector`
- `procedure_not_linked_to_resource_type_detector`
- `ticket_without_assigned_procedure_detector`
- `change_without_effective_time_detector`

Typical anchor:
- `ChangeRequest`
- `TroubleTicket`
- `Procedure`
- `ResourceType`

### `functional_mapping_gap_diagnoser`

Purpose:
- diagnoses incomplete or inconsistent functional traceability in the service-application-resource chain

Intuition:
- anomaly interpretation becomes difficult when applications, modules, services, and resources are incompletely or ambiguously mapped

Main linked level-1 agents:
- `application_without_module_detector`
- `application_without_resource_detector`
- `duplicated_functional_mapping_detector`
- `inconsistent_service_hierarchy_detector`
- `over_concentrated_service_detector`
- `service_without_application_detector`
- `service_without_resource_coverage_detector`

Typical anchor:
- `Application`
- `Service`
- `ApplicationModule`

## A Posteriori Diagnosis Agents

### `single_point_of_failure_diagnoser`

Purpose:
- diagnoses local incident situations where one weak component acts as a single point of failure

Intuition:
- if an incident-related resource is isolated, non-redundant, or attached to incomplete links, and also carries high impact, the local root cause hypothesis becomes strong

Main linked level-1 agents:
- `isolated_incident_resource_detector`
- `incident_on_incomplete_link_detector`
- `high_impact_resource_detector`
- `no_redundancy_incident_detector`
- `child_component_incident_escalation_detector`

Typical anchor:
- `Resource`
- `NetworkLink`

### `change_induced_incident_diagnoser`

Purpose:
- diagnoses change requests as plausible causes or amplifiers of incidents

Intuition:
- a change becomes suspicious when incidents follow it in time, when changes overlap on the same element, when several incidents point back to the same change, or when silent degradation appears afterward

Main linked level-1 agents:
- `change_followed_by_incident_detector`
- `change_overlap_conflict`
- `change_linked_to_multiple_incidents_detector`
- `critical_event_ticket_escalation_detector`
- `silent_degradation_after_change_detector`

Typical anchor:
- `ChangeRequest`
- `RelatedElement`

### `service_cascade_diagnoser`

Purpose:
- diagnoses upward incident propagation through shared service support chains

Intuition:
- one technical issue can affect several services through shared modules, hidden dependencies, repeated service-level incidents, or multi-resource impact

Main linked level-1 agents:
- `cascading_service_failure_detector`
- `hidden_service_dependency_detector`
- `module_level_incident_aggregation_detector`
- `service_impacted_by_multiple_resources_detector`
- `service_with_repeated_incident_detector`
- `incident_propagation_detector`
- `multi_element_synchronous_incident_detector`
- `parent_child_event_escalation_detector`
- `critical_event_ticket_escalation_detector`

Typical anchor:
- `Service`
- `Application`
- `ApplicationModule`
- `Resource`

### `traceability_breakdown_diagnoser`

Purpose:
- diagnoses systemic failures in the incident traceability chain

Intuition:
- incidents become hard to understand and manage when they are not ticketed, when tickets are disconnected from events, or when service impacts are not escalated procedurally

Main linked level-1 agents:
- `incident_without_ticket_detector`
- `ticket_without_linked_event_detector`
- `service_without_ticket_escalation_detector`
- `ticket_without_assigned_procedure_detector`
- `critical_event_ticket_escalation_detector`

Typical anchor:
- operational process scope

### `unstable_component_diagnoser`

Purpose:
- diagnoses recurrent instability rather than one punctual fault

Intuition:
- bursts, repeated events, flapping, reopened incidents, and stale incidents point to chronic unstable behavior

Main linked level-1 agents:
- `event_burst_detector`
- `repeated_similar_event_detector`
- `flapping_state_detector`
- `reopened_incident_detector`
- `stale_incident_detector`

Typical anchor:
- `Resource`
- `Application`
- `TroubleTicket`
- `Event`

### `application_support_failure_diagnoser`

Purpose:
- diagnoses application-level anomalies that are aggravated by broken or contradictory technical support mapping

Intuition:
- an application may look unstable or incident-prone because the support chain behind it is missing, ambiguous, or inconsistent

Main linked level-1 agents:
- `application_incident_without_resource_detector`
- `application_mapping_inconsistency_detector`
- `resource_event_without_service_impact_detector`
- `conflicting_application_state_detector`

Typical anchor:
- `Application`
- `Resource`
- `Service`

### `local_infrastructure_cluster_diagnoser`

Purpose:
- diagnoses disturbed local infrastructure zones rather than isolated unrelated faults

Intuition:
- spatial clusters, parent-child escalation, local propagation, synchronous incidents, and incomplete local topology often indicate a common disturbed area

Main linked level-1 agents:
- `spatial_incident_cluster_detector`
- `parent_child_event_escalation_detector`
- `incident_propagation_detector`
- `multi_element_synchronous_incident_detector`
- `incident_on_incomplete_link_detector`
- `high_impact_resource_detector`

Typical anchor:
- `Location`
- `Resource`
- `NetworkLink`

## Mapping Matrix

The mapping matrix is the main design artifact of level 2.

It is used for:
- conditional activation
- reliability computation
- severity enrichment
- explanation generation

Legend:
- `P` = primary evidence
- `S` = supporting evidence
- `C` = contextual evidence

### A Priori Mapping Matrix

| Level 1 agent | Structural fragility | Critical service exposure | Observability gap | Procedural unreadiness | Functional mapping gap |
|---|---:|---:|---:|---:|---:|
| orphan_resource_detector | P |  |  |  | S |
| missing_interface_detector | P |  |  |  |  |
| orphan_interface_detector | S |  |  |  |  |
| unconnected_interface_detector | P |  |  |  |  |
| incomplete_network_link_detector | P | S |  |  |  |
| missing_parent_resource_detector | S |  |  |  | S |
| application_without_support_detector | P | P |  |  | P |
| unmanaged_resource_detector | S |  |  |  |  |
| missing_redundancy_detector | P | P |  |  |  |
| criticality_structural_weakness_detector | P | P |  |  |  |
| application_without_module_detector |  | S |  |  | P |
| application_without_resource_detector |  | P |  |  | P |
| duplicated_functional_mapping_detector |  | S |  |  | P |
| inconsistent_service_hierarchy_detector |  | S |  |  | P |
| over_concentrated_service_detector | S | P |  |  | S |
| service_without_application_detector |  | P |  |  | P |
| service_without_resource_coverage_detector | S | P |  |  | P |
| change_without_effective_time_detector |  |  | P | S |  |
| event_without_timestamp_detector |  |  | P |  |  |
| event_without_related_element_detector |  |  | P |  | S |
| change_request_without_scheduled_time_detector |  |  | S | P |  |
| procedure_not_linked_to_resource_type_detector |  |  |  | P |  |
| ticket_without_assigned_procedure_detector |  |  |  | P |  |

### A Posteriori Mapping Matrix

| Level 1 agent | Single point of failure | Change-induced incident | Service cascade | Traceability breakdown | Unstable component | Application support failure | Local infrastructure cluster |
|---|---:|---:|---:|---:|---:|---:|---:|
| isolated_incident_resource_detector | P |  | S |  |  |  |  |
| incident_on_incomplete_link_detector | P |  |  |  |  |  | S |
| high_impact_resource_detector | P |  | S |  |  |  | C |
| no_redundancy_incident_detector | P |  | S |  |  |  |  |
| application_mapping_inconsistency_detector |  |  | S |  |  | P |  |
| spatial_incident_cluster_detector |  |  | S |  |  |  | P |
| child_component_incident_escalation_detector | S |  | S |  |  |  | P |
| change_followed_by_incident_detector |  | P | S |  |  |  |  |
| change_overlap_conflict |  | P |  |  |  |  |  |
| critical_event_ticket_escalation_detector |  | S | S | C |  |  |  |
| event_burst_detector |  |  | S |  | P |  | S |
| flapping_state_detector |  |  |  |  | P |  |  |
| incident_propagation_detector | S |  | P |  | S |  | P |
| multi_element_synchronous_incident_detector |  |  | P |  | S |  | P |
| parent_child_event_escalation_detector | S |  | S |  |  |  | P |
| reopened_incident_detector |  |  |  | S | P |  |  |
| repeated_similar_event_detector |  |  |  |  | P |  |  |
| silent_degradation_after_change_detector |  | P | S |  | S |  |  |
| stale_incident_detector |  |  |  | S | P |  |  |
| change_linked_to_multiple_incidents_detector |  | P | S | S |  |  |  |
| incident_without_ticket_detector |  |  |  | P |  |  |  |
| ticket_without_linked_event_detector |  |  |  | P |  |  |  |
| application_incident_without_resource_detector |  |  | S |  |  | P |  |
| cascading_service_failure_detector |  | S | P |  |  | S |  |
| conflicting_application_state_detector |  |  |  |  | S | P |  |
| hidden_service_dependency_detector |  |  | P |  |  | S |  |
| module_level_incident_aggregation_detector |  |  | P |  | S | S |  |
| resource_event_without_service_impact_detector |  |  |  |  |  | P |  |
| service_impacted_by_multiple_resources_detector | S |  | P |  | S |  | S |
| service_without_ticket_escalation_detector |  |  | S | P |  |  |  |
| service_with_repeated_incident_detector |  |  | P |  | S |  |  |

## Execution Logic

The current execution chain is:

1. The mode selected in `mas.properties` activates the corresponding level-1 agents.
2. `level2_controller` waits until all level-1 scripts of the selected mode have reported completion.
3. The controller launches only the level-2 catalogue matching that mode.
4. Each level-2 agent reads its relevant level-1 JSON inputs, evaluates activation, builds diagnosis candidates, computes scores, and exports its result file.
5. In `apriori` mode, the MAS stops automatically after the full level-2 apriori catalogue has finished.

## Notes

- This README documents the current implemented level-2 catalogue and the target reasoning framework defined for MASynReas.
- The mapping matrices are design references. The implementation follows this architecture, but some details may still evolve as the catalogue matures.
- Level 2 is intended to remain deterministic, explainable, and directly grounded in level-1 outputs.
