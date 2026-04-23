$ErrorActionPreference = "Stop"

function Normalize-Text {
    param([string]$Text)
    return ($Text -replace "`r`n", "`n").Trim() + "`n"
}

function Get-SubjectBlock {
    param(
        [string]$Ttl,
        [string]$Subject
    )

    $pattern = "(?ms)^" + [regex]::Escape($Subject) + "\b.*?\.\n(?=\n|$)"
    $match = [regex]::Match($Ttl, $pattern)
    if (-not $match.Success) {
        throw "Subject block not found: $Subject"
    }
    return $match.Value.TrimEnd("`n")
}

function Remove-Subject {
    param(
        [string]$Ttl,
        [string]$Subject
    )

    $pattern = "(?ms)^" + [regex]::Escape($Subject) + "\b.*?\.\n(?=\n|$)"
    return ([regex]::Replace($Ttl, $pattern, "") -replace "\n{3,}", "`n`n").Trim() + "`n"
}

function Append-Block {
    param(
        [string]$Ttl,
        [string]$Block
    )

    return $Ttl.Trim() + "`n`n" + $Block.Trim() + "`n"
}

function Set-SubjectBlock {
    param(
        [string]$Ttl,
        [string]$Subject,
        [string]$NewBlock
    )

    $updated = Remove-Subject -Ttl $Ttl -Subject $Subject
    return Append-Block -Ttl $updated -Block $NewBlock
}

function Update-SubjectBlock {
    param(
        [string]$Ttl,
        [string]$Subject,
        [scriptblock]$Mutator
    )

    $block = Get-SubjectBlock -Ttl $Ttl -Subject $Subject
    $newBlock = & $Mutator $block
    return Set-SubjectBlock -Ttl $Ttl -Subject $Subject -NewBlock $newBlock
}

function Add-BlockIfMissing {
    param(
        [string]$Ttl,
        [string]$Subject,
        [string]$Block
    )

    if ($Ttl -match "(?m)^" + [regex]::Escape($Subject) + "\b") {
        return $Ttl
    }
    return Append-Block -Ttl $Ttl -Block $Block
}

function New-EmptyLevel1 {
    param([hashtable]$L1Detectors)

    $map = [ordered]@{
        apriori = [ordered]@{
            structural = [ordered]@{}
            dynamic = [ordered]@{}
            functional = [ordered]@{}
            procedural = [ordered]@{}
        }
        aposteriori = [ordered]@{
            structural = [ordered]@{}
            dynamic = [ordered]@{}
            functional = [ordered]@{}
            procedural = [ordered]@{}
        }
    }

    foreach ($mode in @("apriori", "aposteriori")) {
        foreach ($family in @("structural", "dynamic", "functional", "procedural")) {
            foreach ($name in $L1Detectors[$mode][$family]) {
                $map[$mode][$family][$name] = @()
            }
        }
    }

    return $map
}

function New-EmptyLevel2 {
    param([hashtable]$L2Diagnosers)

    $map = [ordered]@{
        apriori = [ordered]@{}
        aposteriori = [ordered]@{}
    }

    foreach ($mode in @("apriori", "aposteriori")) {
        foreach ($name in $L2Diagnosers[$mode]) {
            $map[$mode][$name] = @()
        }
    }

    return $map
}

function Apply-L1Expectations {
    param(
        [hashtable]$Target,
        [array]$Expectations
    )

    foreach ($expectation in $Expectations) {
        $Target[$expectation.mode][$expectation.family][$expectation.agent] = @($expectation.items)
    }
}

function Apply-L2Expectations {
    param(
        [hashtable]$Target,
        [array]$Expectations
    )

    foreach ($expectation in $Expectations) {
        $Target[$expectation.mode][$expectation.agent] = @($expectation.items)
    }
}

function Get-NonZeroLevel1Agents {
    param([hashtable]$Level1)

    $agents = @()
    foreach ($mode in @("apriori", "aposteriori")) {
        foreach ($family in @("structural", "dynamic", "functional", "procedural")) {
            foreach ($agent in $Level1[$mode][$family].Keys) {
                if ($Level1[$mode][$family][$agent].Count -gt 0) {
                    $agents += "$mode/$family/$agent"
                }
            }
        }
    }
    return $agents
}

function Get-NonZeroLevel2Diagnosers {
    param([hashtable]$Level2)

    $agents = @()
    foreach ($mode in @("apriori", "aposteriori")) {
        foreach ($agent in $Level2[$mode].Keys) {
            if ($Level2[$mode][$agent].Count -gt 0) {
                $agents += "$mode/$agent"
            }
        }
    }
    return $agents
}

function Get-Level1BindingCount {
    param([hashtable]$Level1)

    $count = 0
    foreach ($mode in @("apriori", "aposteriori")) {
        foreach ($family in @("structural", "dynamic", "functional", "procedural")) {
            foreach ($agent in $Level1[$mode][$family].Keys) {
                $count += $Level1[$mode][$family][$agent].Count
            }
        }
    }
    return $count
}

function Get-Level2DiagnosisCount {
    param([hashtable]$Level2)

    $count = 0
    foreach ($mode in @("apriori", "aposteriori")) {
        foreach ($agent in $Level2[$mode].Keys) {
            $count += $Level2[$mode][$agent].Count
        }
    }
    return $count
}

function Write-Utf8File {
    param(
        [string]$Path,
        [string]$Content
    )

    Set-Content -Path $Path -Value $Content -Encoding utf8
}

function Write-JsonFile {
    param(
        [string]$Path,
        [object]$Data
    )

    $json = $Data | ConvertTo-Json -Depth 12
    Set-Content -Path $Path -Value $json -Encoding utf8
}

function Get-BaseReferenceLink {
    param([string]$BaseGraph)

    if ($BaseGraph -eq "baseA") {
        return "[Base A](C:/Users/rdesb/psc/MASynReas/datasets/baseA/README.md)"
    }
    return "[Base B](C:/Users/rdesb/psc/MASynReas/datasets/baseB/README.md)"
}

function Build-ScenarioReadme {
    param(
        [hashtable]$Scenario,
        [hashtable]$Level1,
        [hashtable]$Level2,
        [string[]]$NonZeroL1,
        [string[]]$NonZeroL2
    )

    $baseLink = Get-BaseReferenceLink -BaseGraph $Scenario.BaseGraph
    $scenarioMode = $Scenario["Mode"]
    $kpiLines = ($Scenario.KpiTargets | ForEach-Object { "- $_" }) -join "`n"
    $mutationLines = ($Scenario.MutationNotes | ForEach-Object { "- $_" }) -join "`n"
    $l1Lines = if ($NonZeroL1.Count -gt 0) {
        ($NonZeroL1 | ForEach-Object { "- $_" }) -join "`n"
    } else {
        "- no level-1 agent should return any binding"
    }
    $l2Lines = if ($NonZeroL2.Count -gt 0) {
        ($NonZeroL2 | ForEach-Object { "- $_" }) -join "`n"
    } else {
        "- no level-2 diagnoser should emit a diagnosis"
    }

    $notes = ($Scenario.Notes | ForEach-Object { "- $_" }) -join "`n"
    $rankingBlock = ""
    if (($Scenario.Keys -contains "RankingExpectation") -and $Scenario.RankingExpectation.Count -gt 0) {
        $rankingLines = ($Scenario.RankingExpectation | ForEach-Object { "- $_" }) -join "`n"
        $rankingBlock = "`n`n## Ranking Expectation`n`n$rankingLines"
    }

    return @"
# $($Scenario.ReadmeTitle)

## Purpose

$($Scenario.Purpose)

## Relation to the Reference Graphs

This scenario is derived from:
- $baseLink

Mode:
- $scenarioMode

## Mutation Profile

$mutationLines

## Contents

Files:
- `dataset.ttl`
- `manifest.json`
- `expected_level1.json`
- `expected_level2.json`

## KPI Targets

$kpiLines

## Expected Level 1 Signals

$l1Lines

## Expected Level 2 Diagnoses

$l2Lines$rankingBlock

## Notes

$notes
"@
}

$datasetsRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $datasetsRoot

$baseAPath = Join-Path $datasetsRoot "baseA\baseA.ttl"
$baseBPath = Join-Path $datasetsRoot "baseB\baseB.ttl"
$ds01Path = Join-Path $datasetsRoot "DS01_clean_baseA\dataset.ttl"

$baseAText = Normalize-Text (Get-Content -Path $baseAPath -Raw)
$baseBText = Normalize-Text (Get-Content -Path $baseBPath -Raw)
$quiescentBaseAText = Normalize-Text (Get-Content -Path $ds01Path -Raw)

$L1Detectors = [ordered]@{
    apriori = [ordered]@{
        structural = @(
            "application_without_support_detector",
            "criticality_structural_weakness_detector",
            "incomplete_network_link_detector",
            "missing_interface_detector",
            "missing_parent_resource_detector",
            "missing_redundancy_detector",
            "orphan_interface_detector",
            "orphan_resource_detector",
            "unconnected_interface_detector",
            "unmanaged_resource_detector"
        )
        dynamic = @(
            "change_without_effective_time_detector",
            "event_without_related_element_detector",
            "event_without_timestamp_detector"
        )
        functional = @(
            "application_without_module_detector",
            "application_without_resource_detector",
            "duplicated_functional_mapping_detector",
            "inconsistent_service_hierarchy_detector",
            "over_concentrated_service_detector",
            "service_without_application_detector",
            "service_without_resource_coverage_detector"
        )
        procedural = @(
            "change_request_without_scheduled_time_detector",
            "procedure_not_linked_to_resource_type_detector",
            "ticket_without_assigned_procedure_detector"
        )
    }
    aposteriori = [ordered]@{
        structural = @(
            "application_mapping_inconsistency_detector",
            "child_component_incident_escalation_detector",
            "high_impact_resource_detector",
            "incident_on_incomplete_link_detector",
            "isolated_incident_resource_detector",
            "no_redundancy_incident_detector",
            "spatial_incident_cluster_detector"
        )
        dynamic = @(
            "change_followed_by_incident_detector",
            "change_overlap_conflict",
            "critical_event_ticket_escalation_detector",
            "event_burst_detector",
            "flapping_state_detector",
            "incident_propagation_detector",
            "multi_element_synchronous_incident_detector",
            "parent_child_event_escalation_detector",
            "reopened_incident_detector",
            "repeated_similar_event_detector",
            "silent_degradation_after_change_detector",
            "stale_incident_detector"
        )
        functional = @(
            "application_incident_without_resource_detector",
            "cascading_service_failure_detector",
            "conflicting_application_state_detector",
            "hidden_service_dependency_detector",
            "module_level_incident_aggregation_detector",
            "resource_event_without_service_impact_detector",
            "service_impacted_by_multiple_resources_detector",
            "service_without_ticket_escalation_detector",
            "service_with_repeated_incident_detector"
        )
        procedural = @(
            "change_linked_to_multiple_incidents_detector",
            "incident_without_ticket_detector",
            "ticket_without_linked_event_detector"
        )
    }
}

$L2Diagnosers = [ordered]@{
    apriori = @(
        "critical_service_exposure_diagnoser",
        "functional_mapping_gap_diagnoser",
        "observability_gap_diagnoser",
        "procedural_unreadiness_diagnoser",
        "structural_fragility_diagnoser"
    )
    aposteriori = @(
        "application_support_failure_diagnoser",
        "change_induced_incident_diagnoser",
        "local_infrastructure_cluster_diagnoser",
        "service_cascade_diagnoser",
        "single_point_of_failure_diagnoser",
        "traceability_breakdown_diagnoser",
        "unstable_component_diagnoser"
    )
}

function Get-QuiescentBaseB {
    $ttl = $baseBText
    foreach ($subject in @(
        "baseB:event_customer_warning",
        "baseB:event_billing_warning",
        "baseB:event_monitoring_warning",
        "baseB:event_workforce_warning",
        "baseB:ticket_customer_warning",
        "baseB:ticket_billing_warning",
        "baseB:ticket_monitoring_warning",
        "baseB:ticket_workforce_warning"
    )) {
        $ttl = Remove-Subject -Ttl $ttl -Subject $subject
    }
    return $ttl
}

$BaseBStatusConcepts = @"
baseB:severity_high
    a skos:Concept ;
    rdfs:label "High"@en .

baseB:priority_high
    a skos:Concept ;
    rdfs:label "High"@en .

baseB:urgency_high
    a skos:Concept ;
    rdfs:label "High"@en .

baseB:status_open
    a skos:Concept ;
    rdfs:label "Open"@en .

baseB:status_resolved
    a skos:Concept ;
    rdfs:label "Resolved"@en .
"@

function Ensure-BaseBStatusConcepts {
    param([string]$Ttl)

    foreach ($subject in @(
        "baseB:severity_high",
        "baseB:priority_high",
        "baseB:urgency_high",
        "baseB:status_open",
        "baseB:status_resolved"
    )) {
        if ($Ttl -notmatch "(?m)^" + [regex]::Escape($subject) + "\b") {
            $Ttl = Append-Block -Ttl $Ttl -Block $BaseBStatusConcepts
            break
        }
    }
    return $Ttl
}

$LargeQuiescentBSnippet = @"
baseB:service_analytics_api
    a noria:Service ;
    rdfs:label "Analytics API Service"@en .

baseB:service_inventory_portal
    a noria:Service ;
    rdfs:label "Inventory Portal Service"@en .

baseB:module_analytics_api
    a noria:ApplicationModule ;
    rdfs:label "Analytics API Module"@en ;
    seas:subSystemOf baseB:service_analytics_api ;
    noria:applicationModuleOf baseB:app_analytics_api .

baseB:module_inventory_portal
    a noria:ApplicationModule ;
    rdfs:label "Inventory Portal Module"@en ;
    seas:subSystemOf baseB:service_inventory_portal ;
    noria:applicationModuleOf baseB:app_inventory_portal .

baseB:app_analytics_api
    a noria:Application ;
    rdfs:label "Analytics API"@en ;
    noria:businessCriticality baseB:criticality_medium .

baseB:app_inventory_portal
    a noria:Application ;
    rdfs:label "Inventory Portal"@en ;
    noria:businessCriticality baseB:criticality_medium .

baseB:res_analytics_vm_01
    a noria:Resource ;
    rdfs:label "Analytics VM 01"@en ;
    noria:resourceType baseB:type_virtual_machine ;
    noria:resourceManagedBy baseB:team_platform ;
    noria:resourceForApplication baseB:app_analytics_api ;
    noria:locatedIn baseB:room_dc1 ;
    seas:subSystemOf baseB:zone_monitoring .

baseB:res_analytics_vm_02
    a noria:Resource ;
    rdfs:label "Analytics VM 02"@en ;
    noria:resourceType baseB:type_virtual_machine ;
    noria:resourceManagedBy baseB:team_platform ;
    noria:resourceForApplication baseB:app_analytics_api ;
    noria:locatedIn baseB:room_dc2 ;
    seas:subSystemOf baseB:zone_monitoring .

baseB:res_inventory_vm_01
    a noria:Resource ;
    rdfs:label "Inventory VM 01"@en ;
    noria:resourceType baseB:type_virtual_machine ;
    noria:resourceManagedBy baseB:team_platform ;
    noria:resourceForApplication baseB:app_inventory_portal ;
    noria:locatedIn baseB:room_dc1 ;
    seas:subSystemOf baseB:zone_workforce .

baseB:res_inventory_vm_02
    a noria:Resource ;
    rdfs:label "Inventory VM 02"@en ;
    noria:resourceType baseB:type_virtual_machine ;
    noria:resourceManagedBy baseB:team_platform ;
    noria:resourceForApplication baseB:app_inventory_portal ;
    noria:locatedIn baseB:room_dc2 ;
    seas:subSystemOf baseB:zone_workforce .

baseB:res_analytics_switch_01
    a noria:Resource ;
    rdfs:label "Analytics Switch 01"@en ;
    noria:resourceType baseB:type_switch ;
    noria:resourceManagedBy baseB:team_network ;
    noria:locatedIn baseB:room_dc1 ;
    seas:subSystemOf baseB:zone_network .

baseB:res_analytics_switch_02
    a noria:Resource ;
    rdfs:label "Analytics Switch 02"@en ;
    noria:resourceType baseB:type_switch ;
    noria:resourceManagedBy baseB:team_network ;
    noria:locatedIn baseB:room_dc2 ;
    seas:subSystemOf baseB:zone_network .

baseB:if_analytics_vm_01
    a noria:NetworkInterface ;
    noria:networkInterfaceOf baseB:res_analytics_vm_01 ;
    noria:networkInterfaceConnects baseB:link_analytics_vm_01_to_switch_01 .

baseB:if_analytics_vm_02
    a noria:NetworkInterface ;
    noria:networkInterfaceOf baseB:res_analytics_vm_02 ;
    noria:networkInterfaceConnects baseB:link_analytics_vm_02_to_switch_02 .

baseB:if_inventory_vm_01
    a noria:NetworkInterface ;
    noria:networkInterfaceOf baseB:res_inventory_vm_01 ;
    noria:networkInterfaceConnects baseB:link_inventory_vm_01_to_switch_01 .

baseB:if_inventory_vm_02
    a noria:NetworkInterface ;
    noria:networkInterfaceOf baseB:res_inventory_vm_02 ;
    noria:networkInterfaceConnects baseB:link_inventory_vm_02_to_switch_02 .

baseB:if_analytics_switch_01_port_01
    a noria:NetworkInterface ;
    noria:networkInterfaceOf baseB:res_analytics_switch_01 ;
    noria:networkInterfaceConnects baseB:link_analytics_vm_01_to_switch_01 .

baseB:if_analytics_switch_01_port_02
    a noria:NetworkInterface ;
    noria:networkInterfaceOf baseB:res_analytics_switch_01 ;
    noria:networkInterfaceConnects baseB:link_inventory_vm_01_to_switch_01 .

baseB:if_analytics_switch_02_port_01
    a noria:NetworkInterface ;
    noria:networkInterfaceOf baseB:res_analytics_switch_02 ;
    noria:networkInterfaceConnects baseB:link_analytics_vm_02_to_switch_02 .

baseB:if_analytics_switch_02_port_02
    a noria:NetworkInterface ;
    noria:networkInterfaceOf baseB:res_analytics_switch_02 ;
    noria:networkInterfaceConnects baseB:link_inventory_vm_02_to_switch_02 .

baseB:link_analytics_vm_01_to_switch_01
    a noria:NetworkLink ;
    noria:networkLinkTerminationResource baseB:res_analytics_vm_01, baseB:res_analytics_switch_01 .

baseB:link_analytics_vm_02_to_switch_02
    a noria:NetworkLink ;
    noria:networkLinkTerminationResource baseB:res_analytics_vm_02, baseB:res_analytics_switch_02 .

baseB:link_inventory_vm_01_to_switch_01
    a noria:NetworkLink ;
    noria:networkLinkTerminationResource baseB:res_inventory_vm_01, baseB:res_analytics_switch_01 .

baseB:link_inventory_vm_02_to_switch_02
    a noria:NetworkLink ;
    noria:networkLinkTerminationResource baseB:res_inventory_vm_02, baseB:res_analytics_switch_02 .
"@

function Get-LargeQuiescentBaseB {
    $ttl = Get-QuiescentBaseB
    return Append-Block -Ttl $ttl -Block $LargeQuiescentBSnippet
}

$scenarios = @(
    [ordered]@{
        Id = "DS01_clean_baseA"
        ReadmeTitle = "DS01 Clean Base A"
        Title = "Clean control scenario derived from Base A"
        BaseGraph = "baseA"
        Mode = "both"
        Source = "quiescentA"
        MutationType = "quiescent_clean_slice"
        Purpose = "This scenario is the clean benchmark control of the catalogue. It keeps the healthy structural, functional, and procedural backbone of Base A and removes the live incident layer so the MAS can be evaluated against a strict false-positive baseline."
        MutationNotes = @(
            "Use the quiescent healthy slice of Base A.",
            "Keep the full support and topology structure intact.",
            "Keep change requests well formed.",
            "Remove all `noria:EventRecord` and `noria:TroubleTicket` instances."
        )
        KpiTargets = @("false_positive_control", "activation_correctness", "baseline_runtime", "traceability_sanity_check")
        InjectedAnomalies = @()
        RemovedEntities = @("baseA:event_customer_warning", "baseA:event_monitoring_warning", "baseA:ticket_customer_warning", "baseA:ticket_monitoring_warning")
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "This is the strongest clean control currently available for the MAS.",
            "It is intentionally quieter than raw Base A to avoid benign aposteriori activations."
        )
        Mutate = { param($ttl) return $ttl }
        L1Expectations = @()
        L2Expectations = @()
    }
    [ordered]@{
        Id = "DS02_partial_evidence_no_l2_v1"
        ReadmeTitle = "DS02 Partial Evidence No L2 V1"
        Title = "Weak isolated evidence without convergent level-2 diagnosis"
        BaseGraph = "baseA"
        Mode = "both"
        Source = "quiescentA"
        MutationType = "weak_partial_signals"
        Purpose = "This scenario introduces a very small number of isolated weak signals. It is intended to verify that level 1 can react locally while level 2 remains silent because there is no convergent diagnostic anchor."
        MutationNotes = @(
            "Remove the actual end time of one change request.",
            "Add one event record without a related element.",
            "Keep the rest of the graph healthy and incident-free."
        )
        KpiTargets = @("activation_correctness", "false_positive_resistance")
        InjectedAnomalies = @("baseA:event_partial_signal")
        RemovedEntities = @()
        RemovedRelations = @("noria:changeRequestActualEndTime on baseA:change_switch_firmware_window")
        NoiseAdditions = @()
        Notes = @(
            "Only two level-1 agents should react.",
            "No level-2 diagnoser should activate."
        )
        Mutate = {
            param($ttl)
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseA:change_switch_firmware_window" -Mutator {
                param($block)
                return $block.Replace("    noria:changeRequestActualEndTime ""2026-01-05T08:20:00Z""^^xsd:dateTime .", ".")
            }
            $ttl = Append-Block -Ttl $ttl -Block @"
baseA:event_partial_signal
    a noria:EventRecord ;
    rdfs:label "Partial signal without related element"@en ;
    noria:loggingTime "2026-01-09T14:00:00Z"^^xsd:dateTime ;
    noria:logText "Weak isolated technical signal without anchored element."@en ;
    dcterms:type baseA:event_type_warning .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "dynamic"; agent = "change_without_effective_time_detector"; items = @([ordered]@{ change = "baseA:change_switch_firmware_window" }) },
            @{ mode = "apriori"; family = "dynamic"; agent = "event_without_related_element_detector"; items = @([ordered]@{ event = "baseA:event_partial_signal" }) }
        )
        L2Expectations = @()
    }
    [ordered]@{
        Id = "DS03_partial_evidence_no_l2_v2"
        ReadmeTitle = "DS03 Partial Evidence No L2 V2"
        Title = "Multi-signal weak evidence without coherent level-2 anchor"
        BaseGraph = "baseA"
        Mode = "both"
        Source = "quiescentA"
        MutationType = "multi_signal_weak_evidence"
        Purpose = "This scenario extends the partial-evidence family with several weak signals on distinct anchors. It checks that the MAS does not overdiagnose when evidence remains fragmented."
        MutationNotes = @(
            "Remove the management link of one switch resource.",
            "Remove the actual end time of a different change request.",
            "Add one event record without timestamp."
        )
        KpiTargets = @("activation_correctness", "false_positive_resistance_under_multi_signal_conditions")
        InjectedAnomalies = @("baseA:event_missing_timestamp")
        RemovedEntities = @()
        RemovedRelations = @(
            "noria:resourceManagedBy on baseA:res_access_switch_02",
            "noria:changeRequestActualEndTime on baseA:change_monitoring_patch"
        )
        NoiseAdditions = @()
        Notes = @(
            "Signals are intentionally distributed across unrelated anchors.",
            "No level-2 diagnoser should aggregate them into a diagnosis."
        )
        Mutate = {
            param($ttl)
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseA:res_access_switch_02" -Mutator {
                param($block)
                return $block.Replace("    noria:resourceManagedBy baseA:team_network ;`n", "")
            }
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseA:change_monitoring_patch" -Mutator {
                param($block)
                return $block.Replace("    noria:changeRequestActualEndTime ""2026-01-07T09:30:00Z""^^xsd:dateTime .", ".")
            }
            $ttl = Append-Block -Ttl $ttl -Block @"
baseA:event_missing_timestamp
    a noria:EventRecord ;
    rdfs:label "Event without timestamp"@en ;
    noria:eventRelatedElement baseA:res_monitor_vm_02 ;
    noria:logOriginatingManagedObject baseA:res_monitor_vm_02 ;
    noria:logOriginatingManagementSystem baseA:app_monitoring_dashboard ;
    noria:alarmProposedRepairAction baseA:procedure_restart_monitoring_agent ;
    noria:logText "Signal emitted without trusted timestamp."@en ;
    dcterms:type baseA:event_type_warning .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "structural"; agent = "unmanaged_resource_detector"; items = @([ordered]@{ resource = "baseA:res_access_switch_02" }) },
            @{ mode = "apriori"; family = "dynamic"; agent = "change_without_effective_time_detector"; items = @([ordered]@{ change = "baseA:change_monitoring_patch" }) },
            @{ mode = "apriori"; family = "dynamic"; agent = "event_without_timestamp_detector"; items = @([ordered]@{ event = "baseA:event_missing_timestamp" }) }
        )
        L2Expectations = @()
    }
    [ordered]@{
        Id = "DS04_structural_fragility_resource_anchor"
        ReadmeTitle = "DS04 Structural Fragility Resource Anchor"
        Title = "A single resource accumulates structural weakness signals"
        BaseGraph = "baseA"
        Mode = "apriori"
        Source = "quiescentA"
        MutationType = "structural_anchor_fragility"
        Purpose = "This scenario is the first integrated apriori diagnosis case. A single resource accumulates enough structural weakness indicators to support the structural fragility diagnoser."
        MutationNotes = @(
            "Remove the management relation of `baseA:res_access_switch_02`.",
            "Remove its structural parent relation.",
            "Remove its two explicit interfaces."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "family_contribution_analysis")
        InjectedAnomalies = @()
        RemovedEntities = @("baseA:if_switch_02_port_01", "baseA:if_switch_02_port_02")
        RemovedRelations = @(
            "noria:resourceManagedBy on baseA:res_access_switch_02",
            "seas:subSystemOf on baseA:res_access_switch_02"
        )
        NoiseAdditions = @()
        Notes = @(
            "The target anchor is the switch resource itself.",
            "This scenario is intentionally apriori-only."
        )
        Mutate = {
            param($ttl)
            $ttl = Remove-Subject -Ttl $ttl -Subject "baseA:if_switch_02_port_01"
            $ttl = Remove-Subject -Ttl $ttl -Subject "baseA:if_switch_02_port_02"
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseA:res_access_switch_02" -Mutator {
                param($block)
                $block = $block.Replace("    noria:resourceManagedBy baseA:team_network ;`n", "")
                $block = $block.Replace("    seas:subSystemOf baseA:network_zone_access ;`n", "")
                return $block
            }
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "structural"; agent = "missing_interface_detector"; items = @([ordered]@{ resource = "baseA:res_access_switch_02" }) },
            @{ mode = "apriori"; family = "structural"; agent = "missing_parent_resource_detector"; items = @([ordered]@{ resource = "baseA:res_access_switch_02" }) },
            @{ mode = "apriori"; family = "structural"; agent = "unmanaged_resource_detector"; items = @([ordered]@{ resource = "baseA:res_access_switch_02" }) }
        )
        L2Expectations = @(
            @{ mode = "apriori"; agent = "structural_fragility_diagnoser"; items = @([ordered]@{ anchor = "baseA:res_access_switch_02"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS05_critical_service_exposure_basic"
        ReadmeTitle = "DS05 Critical Service Exposure Basic"
        Title = "A critical application is reduced to a single visible support resource"
        BaseGraph = "baseA"
        Mode = "apriori"
        Source = "quiescentA"
        MutationType = "critical_support_concentration"
        Purpose = "This scenario creates the basic form of critical service exposure by reducing a critical application and its service chain to a single visible support resource."
        MutationNotes = @(
            "Remove the application support relation from `baseA:res_customer_vm_02` to `baseA:app_customer_portal`.",
            "Keep the service and module chain otherwise healthy."
        )
        KpiTargets = @("precision_at_l2", "severity_score_comparison")
        InjectedAnomalies = @()
        RemovedEntities = @()
        RemovedRelations = @("noria:resourceForApplication from baseA:res_customer_vm_02 to baseA:app_customer_portal")
        NoiseAdditions = @()
        Notes = @(
            "This is the reference case for the critical service exposure severity comparison.",
            "The diagnosis remains focused on the customer portal support chain."
        )
        Mutate = {
            param($ttl)
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseA:res_customer_vm_02" -Mutator {
                param($block)
                return $block.Replace("    noria:resourceForApplication baseA:app_customer_portal ;`n", "")
            }
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "structural"; agent = "missing_redundancy_detector"; items = @([ordered]@{ application = "baseA:app_customer_portal" }) },
            @{ mode = "apriori"; family = "structural"; agent = "criticality_structural_weakness_detector"; items = @([ordered]@{ application = "baseA:app_customer_portal" }) },
            @{ mode = "apriori"; family = "functional"; agent = "over_concentrated_service_detector"; items = @([ordered]@{ service = "baseA:service_customer_access" }) }
        )
        L2Expectations = @(
            @{ mode = "apriori"; agent = "critical_service_exposure_diagnoser"; items = @([ordered]@{ anchor = "baseA:app_customer_portal"; reliability = "medium"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS06_critical_service_exposure_concentrated_service"
        ReadmeTitle = "DS06 Critical Service Exposure Concentrated Service"
        Title = "A stronger critical service exposure case on the same business chain"
        BaseGraph = "baseA"
        Mode = "apriori"
        Source = "quiescentA"
        MutationType = "critical_support_concentration_strong"
        Purpose = "This scenario is a stronger version of DS05. The same critical application is left with a single support resource and that remaining support resource is itself structurally weakened."
        MutationNotes = @(
            "Reuse the single-support mutation of DS05.",
            "Remove the explicit interface of `baseA:res_customer_vm_01`.",
            "Remove its management assignment."
        )
        KpiTargets = @("severity_score_comparison", "priority_score_comparison")
        InjectedAnomalies = @()
        RemovedEntities = @("baseA:if_customer_vm_01")
        RemovedRelations = @(
            "noria:resourceForApplication from baseA:res_customer_vm_02 to baseA:app_customer_portal",
            "noria:resourceManagedBy on baseA:res_customer_vm_01"
        )
        NoiseAdditions = @()
        Notes = @(
            "The expected level-2 diagnosis remains critical service exposure.",
            "Its severity should be higher than in DS05 because the remaining support is also fragile."
        )
        Mutate = {
            param($ttl)
            $ttl = Remove-Subject -Ttl $ttl -Subject "baseA:if_customer_vm_01"
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseA:res_customer_vm_02" -Mutator {
                param($block)
                return $block.Replace("    noria:resourceForApplication baseA:app_customer_portal ;`n", "")
            }
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseA:res_customer_vm_01" -Mutator {
                param($block)
                return $block.Replace("    noria:resourceManagedBy baseA:team_platform ;`n", "")
            }
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "structural"; agent = "missing_redundancy_detector"; items = @([ordered]@{ application = "baseA:app_customer_portal" }) },
            @{ mode = "apriori"; family = "structural"; agent = "criticality_structural_weakness_detector"; items = @([ordered]@{ application = "baseA:app_customer_portal" }) },
            @{ mode = "apriori"; family = "structural"; agent = "missing_interface_detector"; items = @([ordered]@{ resource = "baseA:res_customer_vm_01" }) },
            @{ mode = "apriori"; family = "structural"; agent = "unmanaged_resource_detector"; items = @([ordered]@{ resource = "baseA:res_customer_vm_01" }) },
            @{ mode = "apriori"; family = "functional"; agent = "over_concentrated_service_detector"; items = @([ordered]@{ service = "baseA:service_customer_access" }) }
        )
        L2Expectations = @(
            @{ mode = "apriori"; agent = "critical_service_exposure_diagnoser"; items = @([ordered]@{ anchor = "baseA:app_customer_portal"; reliability = "high"; severity = "high" }) }
        )
    }
    [ordered]@{
        Id = "DS07_observability_gap_events_and_changes"
        ReadmeTitle = "DS07 Observability Gap Events And Changes"
        Title = "Observability and temporal completeness are degraded across events and changes"
        BaseGraph = "baseA"
        Mode = "apriori"
        Source = "quiescentA"
        MutationType = "observability_gap"
        Purpose = "This scenario targets the observability-gap diagnoser by combining incomplete change timing with event records that lack core observability fields."
        MutationNotes = @(
            "Remove the actual end time of both change requests.",
            "Add one event without timestamp.",
            "Add one event without related element."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "reliability_score_calibration")
        InjectedAnomalies = @("baseA:event_obs_missing_timestamp", "baseA:event_obs_missing_related")
        RemovedEntities = @()
        RemovedRelations = @(
            "noria:changeRequestActualEndTime on baseA:change_switch_firmware_window",
            "noria:changeRequestActualEndTime on baseA:change_monitoring_patch"
        )
        NoiseAdditions = @()
        Notes = @(
            "This scenario concentrates on observability, not on service fragility.",
            "The expected level-2 outcome is a single observability-gap diagnosis."
        )
        Mutate = {
            param($ttl)
            foreach ($change in @("baseA:change_switch_firmware_window", "baseA:change_monitoring_patch")) {
                $ttl = Update-SubjectBlock -Ttl $ttl -Subject $change -Mutator {
                    param($block)
                    return ($block -replace "\n\s*noria:changeRequestActualEndTime .*? ;", "") -replace "\n\s*noria:changeRequestActualEndTime .*?\.", ""
                }
            }
            $ttl = Append-Block -Ttl $ttl -Block @"
baseA:event_obs_missing_timestamp
    a noria:EventRecord ;
    rdfs:label "Observability event without timestamp"@en ;
    noria:eventRelatedElement baseA:res_customer_vm_02 ;
    noria:logOriginatingManagedObject baseA:res_customer_vm_02 ;
    noria:logOriginatingManagementSystem baseA:app_customer_portal ;
    noria:alarmProposedRepairAction baseA:procedure_restart_customer_portal ;
    noria:logText "Observability degraded: event ingested without timestamp."@en ;
    dcterms:type baseA:event_type_warning .

baseA:event_obs_missing_related
    a noria:EventRecord ;
    rdfs:label "Observability event without related element"@en ;
    noria:loggingTime "2026-01-08T08:00:00Z"^^xsd:dateTime ;
    noria:logText "Observability degraded: event missing related element."@en ;
    dcterms:type baseA:event_type_warning .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "dynamic"; agent = "change_without_effective_time_detector"; items = @([ordered]@{ change = "baseA:change_switch_firmware_window" }, [ordered]@{ change = "baseA:change_monitoring_patch" }) },
            @{ mode = "apriori"; family = "dynamic"; agent = "event_without_timestamp_detector"; items = @([ordered]@{ event = "baseA:event_obs_missing_timestamp" }) },
            @{ mode = "apriori"; family = "dynamic"; agent = "event_without_related_element_detector"; items = @([ordered]@{ event = "baseA:event_obs_missing_related" }) }
        )
        L2Expectations = @(
            @{ mode = "apriori"; agent = "observability_gap_diagnoser"; items = @([ordered]@{ anchor = "observability_bundle_baseA"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS08_procedural_unreadiness_basic"
        ReadmeTitle = "DS08 Procedural Unreadiness Basic"
        Title = "Operational process readiness is incomplete before any incident diagnosis"
        BaseGraph = "baseA"
        Mode = "apriori"
        Source = "quiescentA"
        MutationType = "procedural_unreadiness"
        Purpose = "This scenario combines missing scheduled change metadata, a ticket without assigned procedure, and unused procedures. Together these signals should activate the procedural unreadiness diagnoser."
        MutationNotes = @(
            "Remove both scheduled time fields from `baseA:change_switch_firmware_window`.",
            "Add one event linked to a new ticket but without proposed repair action.",
            "Keep the existing procedures unused from the event perspective."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "family_contribution_analysis")
        InjectedAnomalies = @("baseA:event_procedural_gap", "baseA:ticket_procedural_gap")
        RemovedEntities = @()
        RemovedRelations = @(
            "noria:plannedStartDate on baseA:change_switch_firmware_window",
            "noria:plannedEndDate on baseA:change_switch_firmware_window"
        )
        NoiseAdditions = @()
        Notes = @(
            "This is an apriori scenario with a lightweight ticketing artifact.",
            "The target diagnosis is procedural unreadiness."
        )
        Mutate = {
            param($ttl)
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseA:change_switch_firmware_window" -Mutator {
                param($block)
                $block = $block.Replace("    noria:plannedStartDate ""2026-01-05T08:00:00Z""^^xsd:dateTime ;`n", "")
                $block = $block.Replace("    noria:plannedEndDate ""2026-01-05T08:30:00Z""^^xsd:dateTime ;`n", "")
                return $block
            }
            $ttl = Append-Block -Ttl $ttl -Block @"
baseA:event_procedural_gap
    a noria:EventRecord ;
    rdfs:label "Procedural gap event"@en ;
    noria:eventRelatedElement baseA:app_customer_portal ;
    noria:logOriginatingManagedObject baseA:res_customer_vm_01 ;
    noria:logOriginatingManagementSystem baseA:app_customer_portal ;
    noria:loggingTime "2026-01-11T09:00:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseA:severity_minor ;
    noria:logText "Ticket raised without associated remediation playbook."@en ;
    dcterms:type baseA:event_type_warning .

baseA:ticket_procedural_gap
    a noria:TroubleTicket ;
    rdfs:label "Procedural gap ticket"@en ;
    noria:troubleTicketTrigger baseA:event_procedural_gap ;
    dcterms:relation baseA:event_procedural_gap ;
    noria:troubleTicketImpacts baseA:app_customer_portal ;
    noria:troubleTicketRelatedResource baseA:res_customer_vm_01 ;
    noria:troubleTicketDetectionDateTime "2026-01-11T09:10:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseA:status_closed ;
    noria:troubleTicketSeverity baseA:severity_minor ;
    noria:troubleTicketPriority baseA:priority_normal ;
    noria:troubleTicketUrgency baseA:urgency_normal .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "procedural"; agent = "change_request_without_scheduled_time_detector"; items = @([ordered]@{ change = "baseA:change_switch_firmware_window" }) },
            @{ mode = "apriori"; family = "procedural"; agent = "procedure_not_linked_to_resource_type_detector"; items = @([ordered]@{ procedure = "baseA:procedure_restart_customer_portal" }, [ordered]@{ procedure = "baseA:procedure_restart_monitoring_agent" }) },
            @{ mode = "apriori"; family = "procedural"; agent = "ticket_without_assigned_procedure_detector"; items = @([ordered]@{ ticket = "baseA:ticket_procedural_gap" }) }
        )
        L2Expectations = @(
            @{ mode = "apriori"; agent = "procedural_unreadiness_diagnoser"; items = @([ordered]@{ anchor = "baseA:ticket_procedural_gap"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS09_functional_mapping_gap_application_chain"
        ReadmeTitle = "DS09 Functional Mapping Gap Application Chain"
        Title = "A service loses its visible application-module mapping chain"
        BaseGraph = "baseA"
        Mode = "apriori"
        Source = "quiescentA"
        MutationType = "functional_mapping_gap"
        Purpose = "This scenario targets the functional mapping gap diagnoser by breaking the service -> module -> application chain of one business service."
        MutationNotes = @(
            "Remove `baseA:module_customer_portal`.",
            "Leave the application and resource support in place so the break is localized in the functional layer."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2")
        InjectedAnomalies = @()
        RemovedEntities = @("baseA:module_customer_portal")
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "The functional chain should break without altering the technical support graph.",
            "The expected diagnosis is functional mapping gap."
        )
        Mutate = {
            param($ttl)
            return Remove-Subject -Ttl $ttl -Subject "baseA:module_customer_portal"
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "functional"; agent = "application_without_module_detector"; items = @([ordered]@{ application = "baseA:app_customer_portal" }) },
            @{ mode = "apriori"; family = "functional"; agent = "service_without_application_detector"; items = @([ordered]@{ service = "baseA:service_customer_access" }) },
            @{ mode = "apriori"; family = "functional"; agent = "service_without_resource_coverage_detector"; items = @([ordered]@{ service = "baseA:service_customer_access" }) }
        )
        L2Expectations = @(
            @{ mode = "apriori"; agent = "functional_mapping_gap_diagnoser"; items = @([ordered]@{ anchor = "baseA:service_customer_access"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS10_apriori_mixed_two_true_diagnoses"
        ReadmeTitle = "DS10 Apriori Mixed Two True Diagnoses"
        Title = "Two independent apriori diagnosis families coexist in the same graph"
        BaseGraph = "baseA"
        Mode = "apriori"
        Source = "quiescentA"
        MutationType = "mixed_apriori_multi_diagnosis"
        Purpose = "This scenario is the first mixed apriori benchmark. One part of the graph should trigger critical service exposure and another should trigger functional mapping gap."
        MutationNotes = @(
            "Reduce the customer portal support chain to one resource.",
            "Remove the monitoring dashboard module to break the monitoring service functional chain."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "top1_diagnosis_accuracy", "family_contribution_analysis")
        InjectedAnomalies = @()
        RemovedEntities = @("baseA:module_monitoring_dashboard")
        RemovedRelations = @("noria:resourceForApplication from baseA:res_customer_vm_02 to baseA:app_customer_portal")
        NoiseAdditions = @()
        Notes = @(
            "The two target diagnoses are intentionally independent.",
            "This is a useful early ranking scenario for the apriori layer."
        )
        Mutate = {
            param($ttl)
            $ttl = Remove-Subject -Ttl $ttl -Subject "baseA:module_monitoring_dashboard"
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseA:res_customer_vm_02" -Mutator {
                param($block)
                return $block.Replace("    noria:resourceForApplication baseA:app_customer_portal ;`n", "")
            }
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "structural"; agent = "missing_redundancy_detector"; items = @([ordered]@{ application = "baseA:app_customer_portal" }) },
            @{ mode = "apriori"; family = "structural"; agent = "criticality_structural_weakness_detector"; items = @([ordered]@{ application = "baseA:app_customer_portal" }) },
            @{ mode = "apriori"; family = "functional"; agent = "over_concentrated_service_detector"; items = @([ordered]@{ service = "baseA:service_customer_access" }) },
            @{ mode = "apriori"; family = "functional"; agent = "application_without_module_detector"; items = @([ordered]@{ application = "baseA:app_monitoring_dashboard" }) },
            @{ mode = "apriori"; family = "functional"; agent = "service_without_application_detector"; items = @([ordered]@{ service = "baseA:service_network_monitoring" }) },
            @{ mode = "apriori"; family = "functional"; agent = "service_without_resource_coverage_detector"; items = @([ordered]@{ service = "baseA:service_network_monitoring" }) }
        )
        L2Expectations = @(
            @{ mode = "apriori"; agent = "critical_service_exposure_diagnoser"; items = @([ordered]@{ anchor = "baseA:app_customer_portal"; reliability = "medium"; severity = "medium" }) },
            @{ mode = "apriori"; agent = "functional_mapping_gap_diagnoser"; items = @([ordered]@{ anchor = "baseA:service_network_monitoring"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS11_single_point_of_failure_basic"
        ReadmeTitle = "DS11 Single Point Of Failure Basic"
        Title = "An incident reveals a structurally exposed single point of failure"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "single_point_of_failure"
        Purpose = "This scenario concentrates several structural aposteriori clues on one infrastructure element so the MAS can recognize a single point of failure."
        MutationNotes = @(
            "Reduce `baseB:res_firewall_01` to a single incomplete visible link.",
            "Add dependent child resources under `baseB:res_firewall_01` to make it high impact.",
            "Add one high-severity open ticket directly impacting `baseB:res_firewall_01`."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "top1_diagnosis_accuracy")
        InjectedAnomalies = @("baseB:event_firewall_major", "baseB:ticket_firewall_major")
        RemovedEntities = @("baseB:if_workforce_vm_01", "baseB:if_firewall_01_port_02", "baseB:link_workforce_vm_01_to_firewall_01", "baseB:if_monitor_vm_01")
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "The target anchor is `baseB:res_firewall_01`.",
            "This scenario is designed to support a single dominant level-2 diagnosis."
        )
        Mutate = {
            param($ttl)
            $ttl = Ensure-BaseBStatusConcepts -Ttl $ttl
            foreach ($subject in @("baseB:if_workforce_vm_01", "baseB:if_firewall_01_port_02", "baseB:link_workforce_vm_01_to_firewall_01", "baseB:if_monitor_vm_01")) {
                $ttl = Remove-Subject -Ttl $ttl -Subject $subject
            }
            $ttl = Append-Block -Ttl $ttl -Block @"
baseB:res_firewall_rulecard_01
    a noria:Resource ;
    rdfs:label "Firewall rule card 01"@en ;
    noria:partOf baseB:res_firewall_01 .

baseB:res_firewall_rulecard_02
    a noria:Resource ;
    rdfs:label "Firewall rule card 02"@en ;
    noria:partOf baseB:res_firewall_01 .

baseB:res_firewall_rulecard_03
    a noria:Resource ;
    rdfs:label "Firewall rule card 03"@en ;
    noria:partOf baseB:res_firewall_01 .

baseB:event_firewall_major
    a noria:EventRecord ;
    rdfs:label "Firewall major incident"@en ;
    noria:eventRelatedElement baseB:res_firewall_01 ;
    noria:logOriginatingManagedObject baseB:res_firewall_01 ;
    noria:loggingTime "2026-02-11T09:00:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_high ;
    noria:logText "Critical outage detected on firewall 01."@en ;
    dcterms:type baseB:event_type_warning .

baseB:ticket_firewall_major
    a noria:TroubleTicket ;
    rdfs:label "Firewall major incident ticket"@en ;
    noria:troubleTicketTrigger baseB:event_firewall_major ;
    dcterms:relation baseB:event_firewall_major ;
    noria:troubleTicketImpacts baseB:res_firewall_01 ;
    noria:troubleTicketRelatedResource baseB:res_firewall_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-11T09:05:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_open ;
    noria:troubleTicketSeverity baseB:severity_high ;
    noria:troubleTicketPriority baseB:priority_high ;
    noria:troubleTicketUrgency baseB:urgency_high .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "structural"; agent = "isolated_incident_resource_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_01" }) },
            @{ mode = "aposteriori"; family = "structural"; agent = "incident_on_incomplete_link_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_01"; link = "baseB:link_monitor_vm_01_to_firewall_01" }) },
            @{ mode = "aposteriori"; family = "structural"; agent = "no_redundancy_incident_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_01" }) },
            @{ mode = "aposteriori"; family = "structural"; agent = "high_impact_resource_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_01" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "single_point_of_failure_diagnoser"; items = @([ordered]@{ anchor = "baseB:res_firewall_01"; reliability = "high"; severity = "high" }) }
        )
    }
    [ordered]@{
        Id = "DS12_change_induced_incident_basic"
        ReadmeTitle = "DS12 Change Induced Incident Basic"
        Title = "A recent change is followed by a high-severity incident on the same element"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "change_induced_incident"
        Purpose = "This scenario creates a clear post-change anomaly pattern: overlapping changes on one application are followed by a critical event and an escalated ticket on that same application."
        MutationNotes = @(
            "Add an overlapping hotfix change on `baseB:app_customer_portal`.",
            "Add a critical event shortly after the end of the release change.",
            "Add an open high-priority ticket triggered by that event."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "top1_diagnosis_accuracy")
        InjectedAnomalies = @("baseB:change_customer_hotfix", "baseB:event_customer_post_change", "baseB:ticket_customer_post_change")
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "The target diagnosis is change-induced incident.",
            "This scenario is suitable for validating temporal explanation chains."
        )
        Mutate = {
            param($ttl)
            $ttl = Ensure-BaseBStatusConcepts -Ttl $ttl
            $ttl = Append-Block -Ttl $ttl -Block @"
baseB:change_customer_hotfix
    a noria:ChangeRequest ;
    rdfs:label "Customer portal hotfix"@en ;
    noria:eventRelatedElement baseB:app_customer_portal ;
    noria:plannedStartDate "2026-02-06T09:15:00Z"^^xsd:dateTime ;
    noria:plannedEndDate "2026-02-06T10:00:00Z"^^xsd:dateTime ;
    noria:changeRequestActualStartTime "2026-02-06T09:20:00Z"^^xsd:dateTime ;
    noria:changeRequestActualEndTime "2026-02-06T09:50:00Z"^^xsd:dateTime .

baseB:event_customer_post_change
    a noria:EventRecord ;
    rdfs:label "Post-change customer incident"@en ;
    noria:eventRelatedElement baseB:app_customer_portal ;
    noria:logOriginatingManagedObject baseB:res_customer_vm_01 ;
    noria:logOriginatingManagementSystem baseB:app_customer_portal ;
    noria:loggingTime "2026-02-06T09:40:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_high ;
    noria:logText "Critical outage detected right after customer portal changes."@en ;
    dcterms:type baseB:event_type_warning .

baseB:ticket_customer_post_change
    a noria:TroubleTicket ;
    rdfs:label "Post-change customer incident ticket"@en ;
    noria:troubleTicketTrigger baseB:event_customer_post_change ;
    dcterms:relation baseB:event_customer_post_change ;
    noria:troubleTicketImpacts baseB:app_customer_portal ;
    noria:troubleTicketDetectionDateTime "2026-02-06T09:45:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_open ;
    noria:troubleTicketSeverity baseB:severity_high ;
    noria:troubleTicketPriority baseB:priority_high ;
    noria:troubleTicketUrgency baseB:urgency_high .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "dynamic"; agent = "change_followed_by_incident_detector"; items = @([ordered]@{ change = "baseB:change_customer_release"; event = "baseB:event_customer_post_change" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "change_overlap_conflict"; items = @([ordered]@{ change1 = "baseB:change_customer_release"; change2 = "baseB:change_customer_hotfix" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "critical_event_ticket_escalation_detector"; items = @([ordered]@{ event = "baseB:event_customer_post_change"; ticket = "baseB:ticket_customer_post_change" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "change_induced_incident_diagnoser"; items = @([ordered]@{ anchor = "baseB:app_customer_portal"; reliability = "high"; severity = "high" }) }
        )
    }
    [ordered]@{
        Id = "DS13_service_cascade_basic"
        ReadmeTitle = "DS13 Service Cascade Basic"
        Title = "A shared functional dependency lets one technical issue affect several services"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "service_cascade"
        Purpose = "This scenario creates a hidden service dependency by attaching the same module to two services. Existing monitoring events should then support a service-cascade diagnosis."
        MutationNotes = @(
            "Add a second service parent to `baseB:module_monitoring_dashboard`.",
            "Reuse the existing monitoring event chain."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "family_contribution_analysis")
        InjectedAnomalies = @()
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "The scenario intentionally reuses healthy operational data from Base B.",
            "The diagnosis comes from hidden functional coupling, not from extra noise."
        )
        Mutate = {
            param($ttl)
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseB:module_monitoring_dashboard" -Mutator {
                param($block)
                return $block.Replace(
                    "    seas:subSystemOf baseB:service_network_monitoring ;",
                    "    seas:subSystemOf baseB:service_network_monitoring ;`n    seas:subSystemOf baseB:service_workforce_portal ;"
                )
            }
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "functional"; agent = "hidden_service_dependency_detector"; items = @([ordered]@{ service_a = "baseB:service_network_monitoring"; service_b = "baseB:service_workforce_portal" }) },
            @{ mode = "aposteriori"; family = "functional"; agent = "cascading_service_failure_detector"; items = @([ordered]@{ module = "baseB:module_monitoring_dashboard"; resource = "baseB:res_monitor_vm_01" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "service_cascade_diagnoser"; items = @([ordered]@{ anchor = "baseB:module_monitoring_dashboard"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS14_traceability_breakdown_basic"
        ReadmeTitle = "DS14 Traceability Breakdown Basic"
        Title = "The event-to-ticket traceability chain is broken for one incident"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "traceability_breakdown"
        Purpose = "This scenario removes the explicit event-ticket links for one incident so that the procedural aposteriori family can detect a traceability breakdown."
        MutationNotes = @(
            "Remove the trigger and relation links from `baseB:ticket_billing_warning` to `baseB:event_billing_warning`.",
            "Keep the rest of the billing incident context intact."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "traceability_sanity_check")
        InjectedAnomalies = @()
        RemovedEntities = @()
        RemovedRelations = @(
            "noria:troubleTicketTrigger on baseB:ticket_billing_warning",
            "dcterms:relation on baseB:ticket_billing_warning"
        )
        NoiseAdditions = @()
        Notes = @(
            "One event becomes ticketless from the graph perspective.",
            "One ticket becomes eventless from the graph perspective."
        )
        Mutate = {
            param($ttl)
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseB:ticket_billing_warning" -Mutator {
                param($block)
                $block = $block.Replace("    noria:troubleTicketTrigger baseB:event_billing_warning ;`n", "")
                $block = $block.Replace("    dcterms:relation baseB:event_billing_warning ;`n", "")
                return $block
            }
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "procedural"; agent = "incident_without_ticket_detector"; items = @([ordered]@{ event = "baseB:event_billing_warning" }) },
            @{ mode = "aposteriori"; family = "procedural"; agent = "ticket_without_linked_event_detector"; items = @([ordered]@{ ticket = "baseB:ticket_billing_warning" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "traceability_breakdown_diagnoser"; items = @([ordered]@{ anchor = "baseB:app_billing_gateway"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS15_unstable_component_basic"
        ReadmeTitle = "DS15 Unstable Component Basic"
        Title = "Repeated and contradictory symptoms accumulate on one monitored component"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "unstable_component"
        Purpose = "This scenario creates a classic unstable-component pattern with bursts of follow-up events, contradictory states, and recurrent ticketing on the same anchor."
        MutationNotes = @(
            "Add several close-in-time monitoring events on `baseB:res_monitor_vm_01`.",
            "Add one resolved ticket followed by a new open ticket on the same element.",
            "Keep timestamps old enough to satisfy the stale-incident heuristic."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "priority_score_calibration")
        InjectedAnomalies = @("baseB:event_monitor_down", "baseB:event_monitor_up", "baseB:event_monitor_timeout", "baseB:event_monitor_timeout_repeat", "baseB:ticket_monitor_resolved_old", "baseB:ticket_monitor_active_new")
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "The target anchor is `baseB:res_monitor_vm_01`.",
            "This scenario is useful for validating temporal instability aggregation."
        )
        Mutate = {
            param($ttl)
            $ttl = Ensure-BaseBStatusConcepts -Ttl $ttl
            $ttl = Append-Block -Ttl $ttl -Block @"
baseB:event_monitor_down
    a noria:EventRecord ;
    rdfs:label "Monitoring component down"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:00:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_high ;
    noria:logText "down"@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_monitor_up
    a noria:EventRecord ;
    rdfs:label "Monitoring component up"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:02:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_minor ;
    noria:logText "up restored"@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_monitor_timeout
    a noria:EventRecord ;
    rdfs:label "Monitoring component timeout"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:03:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_minor ;
    noria:logText "timeout intermittent retry"@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_monitor_timeout_repeat
    a noria:EventRecord ;
    rdfs:label "Monitoring component timeout repeat"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:04:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_minor ;
    noria:logText "timeout intermittent retry"@en ;
    dcterms:type baseB:event_type_warning .

baseB:ticket_monitor_resolved_old
    a noria:TroubleTicket ;
    rdfs:label "Resolved monitor incident ticket"@en ;
    noria:troubleTicketImpacts baseB:res_monitor_vm_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-15T09:30:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_resolved .

baseB:ticket_monitor_active_new
    a noria:TroubleTicket ;
    rdfs:label "Reopened monitor incident ticket"@en ;
    noria:troubleTicketImpacts baseB:res_monitor_vm_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-16T10:01:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_open ;
    noria:troubleTicketSeverity baseB:severity_high ;
    noria:troubleTicketPriority baseB:priority_high ;
    noria:troubleTicketUrgency baseB:urgency_high .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "dynamic"; agent = "event_burst_detector"; items = @([ordered]@{ element = "baseB:res_monitor_vm_01" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "flapping_state_detector"; items = @([ordered]@{ element = "baseB:res_monitor_vm_01" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "repeated_similar_event_detector"; items = @([ordered]@{ element = "baseB:res_monitor_vm_01" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "reopened_incident_detector"; items = @([ordered]@{ relatedElement = "baseB:res_monitor_vm_01" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "stale_incident_detector"; items = @([ordered]@{ relatedElement = "baseB:res_monitor_vm_01" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "unstable_component_diagnoser"; items = @([ordered]@{ anchor = "baseB:res_monitor_vm_01"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS16_application_support_failure_basic"
        ReadmeTitle = "DS16 Application Support Failure Basic"
        Title = "An incidented application loses its visible technical support mapping"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "application_support_failure"
        Purpose = "This scenario removes the visible support resources of one application while keeping its incident chain. The resulting ambiguity should support the application-support-failure diagnosis."
        MutationNotes = @(
            "Remove both support relations from the billing application nodes.",
            "Keep the billing event and ticket chain intact."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "family_contribution_analysis")
        InjectedAnomalies = @()
        RemovedEntities = @()
        RemovedRelations = @(
            "noria:resourceForApplication on baseB:res_billing_api_01",
            "noria:resourceForApplication on baseB:res_billing_api_02"
        )
        NoiseAdditions = @()
        Notes = @(
            "The billing application remains incidented but unsupported in the visible graph.",
            "This should activate both structural and functional aposteriori families."
        )
        Mutate = {
            param($ttl)
            foreach ($resource in @("baseB:res_billing_api_01", "baseB:res_billing_api_02")) {
                $ttl = Update-SubjectBlock -Ttl $ttl -Subject $resource -Mutator {
                    param($block)
                    return $block.Replace("    noria:resourceForApplication baseB:app_billing_gateway ;`n", "")
                }
            }
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "structural"; agent = "application_mapping_inconsistency_detector"; items = @([ordered]@{ application = "baseB:app_billing_gateway" }) },
            @{ mode = "aposteriori"; family = "functional"; agent = "application_incident_without_resource_detector"; items = @([ordered]@{ application = "baseB:app_billing_gateway" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "application_support_failure_diagnoser"; items = @([ordered]@{ anchor = "baseB:app_billing_gateway"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS17_local_infrastructure_cluster_basic"
        ReadmeTitle = "DS17 Local Infrastructure Cluster Basic"
        Title = "Several incident signals concentrate in the same location and time window"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "local_infrastructure_cluster"
        Purpose = "This scenario creates a local infrastructure cluster by adding several synchronous incident chains on elements co-located in the same room."
        MutationNotes = @(
            "Reuse the existing customer warning event in room DC1.",
            "Add billing and access-switch incident chains in the same room within the same short time window."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "top1_diagnosis_accuracy")
        InjectedAnomalies = @("baseB:event_billing_cluster", "baseB:event_switch_cluster", "baseB:ticket_billing_cluster", "baseB:ticket_switch_cluster")
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "The main target is the location cluster in room DC1.",
            "This scenario is useful for validating localization-aware diagnosis."
        )
        Mutate = {
            param($ttl)
            $ttl = Ensure-BaseBStatusConcepts -Ttl $ttl
            $ttl = Append-Block -Ttl $ttl -Block @"
baseB:event_billing_cluster
    a noria:EventRecord ;
    rdfs:label "Billing cluster event"@en ;
    noria:eventRelatedElement baseB:res_billing_api_01 ;
    noria:logOriginatingManagedObject baseB:res_billing_api_01 ;
    noria:logOriginatingManagementSystem baseB:app_billing_gateway ;
    noria:loggingTime "2026-02-10T10:02:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_high ;
    noria:logText "Critical local issue on billing node in room DC1."@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_switch_cluster
    a noria:EventRecord ;
    rdfs:label "Access switch cluster event"@en ;
    noria:eventRelatedElement baseB:res_access_switch_01 ;
    noria:logOriginatingManagedObject baseB:res_access_switch_01 ;
    noria:loggingTime "2026-02-10T10:03:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_high ;
    noria:logText "Critical local issue on switch 01 in room DC1."@en ;
    dcterms:type baseB:event_type_warning .

baseB:ticket_billing_cluster
    a noria:TroubleTicket ;
    rdfs:label "Billing cluster ticket"@en ;
    noria:troubleTicketTrigger baseB:event_billing_cluster ;
    dcterms:relation baseB:event_billing_cluster ;
    noria:troubleTicketImpacts baseB:res_billing_api_01 ;
    noria:troubleTicketRelatedResource baseB:res_billing_api_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-10T10:04:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_open ;
    noria:troubleTicketSeverity baseB:severity_high ;
    noria:troubleTicketPriority baseB:priority_high ;
    noria:troubleTicketUrgency baseB:urgency_high .

baseB:ticket_switch_cluster
    a noria:TroubleTicket ;
    rdfs:label "Switch cluster ticket"@en ;
    noria:troubleTicketTrigger baseB:event_switch_cluster ;
    dcterms:relation baseB:event_switch_cluster ;
    noria:troubleTicketImpacts baseB:res_access_switch_01 ;
    noria:troubleTicketRelatedResource baseB:res_access_switch_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-10T10:05:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_open ;
    noria:troubleTicketSeverity baseB:severity_high ;
    noria:troubleTicketPriority baseB:priority_high ;
    noria:troubleTicketUrgency baseB:urgency_high .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "structural"; agent = "spatial_incident_cluster_detector"; items = @([ordered]@{ location = "baseB:room_dc1" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "multi_element_synchronous_incident_detector"; items = @([ordered]@{ window = "2026-02-10T10:00:00Z" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "local_infrastructure_cluster_diagnoser"; items = @([ordered]@{ anchor = "baseB:room_dc1"; reliability = "high"; severity = "high" }) }
        )
    }
    [ordered]@{
        Id = "DS18_aposteriori_mixed_two_true_diagnoses"
        ReadmeTitle = "DS18 Aposteriori Mixed Two True Diagnoses"
        Title = "Two independent aposteriori diagnosis families coexist"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "mixed_aposteriori_multi_diagnosis"
        Purpose = "This scenario mixes a service-cascade pattern with an unstable-component pattern so the level-2 layer must separate two true diagnoses."
        MutationNotes = @(
            "Create the shared monitoring/workforce module dependency from DS13.",
            "Create the unstable monitor component timeline from DS15."
        )
        KpiTargets = @("precision_at_l2", "recall_at_l2", "top1_diagnosis_accuracy", "mrr", "family_contribution_analysis")
        InjectedAnomalies = @("baseB:event_monitor_down", "baseB:event_monitor_up", "baseB:event_monitor_timeout", "baseB:event_monitor_timeout_repeat", "baseB:ticket_monitor_resolved_old", "baseB:ticket_monitor_active_new")
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "The two intended diagnoses should remain distinguishable.",
            "This is a key mixed scenario for ranking quality."
        )
        Mutate = {
            param($ttl)
            $ttl = Ensure-BaseBStatusConcepts -Ttl $ttl
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseB:module_monitoring_dashboard" -Mutator {
                param($block)
                return $block.Replace(
                    "    seas:subSystemOf baseB:service_network_monitoring ;",
                    "    seas:subSystemOf baseB:service_network_monitoring ;`n    seas:subSystemOf baseB:service_workforce_portal ;"
                )
            }
            $ttl = Append-Block -Ttl $ttl -Block @"
baseB:event_monitor_down
    a noria:EventRecord ;
    rdfs:label "Monitoring component down"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:00:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_high ;
    noria:logText "down"@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_monitor_up
    a noria:EventRecord ;
    rdfs:label "Monitoring component up"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:02:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_minor ;
    noria:logText "up restored"@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_monitor_timeout
    a noria:EventRecord ;
    rdfs:label "Monitoring component timeout"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:03:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_minor ;
    noria:logText "timeout intermittent retry"@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_monitor_timeout_repeat
    a noria:EventRecord ;
    rdfs:label "Monitoring component timeout repeat"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:04:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_minor ;
    noria:logText "timeout intermittent retry"@en ;
    dcterms:type baseB:event_type_warning .

baseB:ticket_monitor_resolved_old
    a noria:TroubleTicket ;
    rdfs:label "Resolved monitor incident ticket"@en ;
    noria:troubleTicketImpacts baseB:res_monitor_vm_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-15T09:30:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_resolved .

baseB:ticket_monitor_active_new
    a noria:TroubleTicket ;
    rdfs:label "Reopened monitor incident ticket"@en ;
    noria:troubleTicketImpacts baseB:res_monitor_vm_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-16T10:01:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_open ;
    noria:troubleTicketSeverity baseB:severity_high ;
    noria:troubleTicketPriority baseB:priority_high ;
    noria:troubleTicketUrgency baseB:urgency_high .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "functional"; agent = "hidden_service_dependency_detector"; items = @([ordered]@{ service_a = "baseB:service_network_monitoring"; service_b = "baseB:service_workforce_portal" }) },
            @{ mode = "aposteriori"; family = "functional"; agent = "cascading_service_failure_detector"; items = @([ordered]@{ module = "baseB:module_monitoring_dashboard" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "event_burst_detector"; items = @([ordered]@{ element = "baseB:res_monitor_vm_01" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "flapping_state_detector"; items = @([ordered]@{ element = "baseB:res_monitor_vm_01" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "reopened_incident_detector"; items = @([ordered]@{ relatedElement = "baseB:res_monitor_vm_01" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "service_cascade_diagnoser"; items = @([ordered]@{ anchor = "baseB:module_monitoring_dashboard"; reliability = "high"; severity = "medium" }) },
            @{ mode = "aposteriori"; agent = "unstable_component_diagnoser"; items = @([ordered]@{ anchor = "baseB:res_monitor_vm_01"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS19_missing_data_structural_and_temporal"
        ReadmeTitle = "DS19 Missing Data Structural And Temporal"
        Title = "Structural and temporal information is degraded without creating a full diagnosis"
        BaseGraph = "baseB"
        Mode = "both"
        Source = "baseB"
        MutationType = "missing_data_robustness"
        Purpose = "This robustness scenario removes a few key structural and temporal facts from an otherwise healthy operational graph. The point is to observe graceful degradation rather than a strong diagnosis."
        MutationNotes = @(
            "Remove the timestamp of `baseB:event_monitoring_warning`.",
            "Remove the related element of `baseB:event_workforce_warning`.",
            "Remove the explicit interface of `baseB:res_billing_api_02`."
        )
        KpiTargets = @("missing_data_robustness", "activation_correctness")
        InjectedAnomalies = @()
        RemovedEntities = @("baseB:if_billing_api_02")
        RemovedRelations = @(
            "noria:loggingTime on baseB:event_monitoring_warning",
            "noria:eventRelatedElement on baseB:event_workforce_warning"
        )
        NoiseAdditions = @()
        Notes = @(
            "This scenario is intended to stay below a strong level-2 diagnosis threshold.",
            "It is mainly a robustness probe for level-1 behavior."
        )
        Mutate = {
            param($ttl)
            $ttl = Remove-Subject -Ttl $ttl -Subject "baseB:if_billing_api_02"
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseB:event_monitoring_warning" -Mutator {
                param($block)
                return $block.Replace("    noria:loggingTime ""2026-02-15T09:20:00Z""^^xsd:dateTime ;`n", "")
            }
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseB:event_workforce_warning" -Mutator {
                param($block)
                return $block.Replace("    noria:eventRelatedElement baseB:res_workforce_vm_01 ;`n", "")
            }
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "structural"; agent = "missing_interface_detector"; items = @([ordered]@{ resource = "baseB:res_billing_api_02" }) },
            @{ mode = "apriori"; family = "dynamic"; agent = "event_without_timestamp_detector"; items = @([ordered]@{ event = "baseB:event_monitoring_warning" }) },
            @{ mode = "apriori"; family = "dynamic"; agent = "event_without_related_element_detector"; items = @([ordered]@{ event = "baseB:event_workforce_warning" }) }
        )
        L2Expectations = @()
    }
    [ordered]@{
        Id = "DS20_missing_procedural_links"
        ReadmeTitle = "DS20 Missing Procedural Links"
        Title = "Operational artifacts exist but key procedural links are missing"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "missing_procedural_links"
        Purpose = "This scenario removes ticket-event links on two incident chains. The incidents remain visible, but the procedural traceability layer is weakened."
        MutationNotes = @(
            "Remove trigger and relation links from the customer and workforce tickets.",
            "Keep the events and the tickets themselves."
        )
        KpiTargets = @("missing_data_robustness", "traceability_robustness")
        InjectedAnomalies = @()
        RemovedEntities = @()
        RemovedRelations = @(
            "noria:troubleTicketTrigger and dcterms:relation on baseB:ticket_customer_warning",
            "noria:troubleTicketTrigger and dcterms:relation on baseB:ticket_workforce_warning"
        )
        NoiseAdditions = @()
        Notes = @(
            "The expected level-2 outcome is traceability breakdown.",
            "This scenario is useful for robustness comparisons against complete incident chains."
        )
        Mutate = {
            param($ttl)
            foreach ($ticket in @(
                @{ subject = "baseB:ticket_customer_warning"; event = "baseB:event_customer_warning" },
                @{ subject = "baseB:ticket_workforce_warning"; event = "baseB:event_workforce_warning" }
            )) {
                $ttl = Update-SubjectBlock -Ttl $ttl -Subject $ticket.subject -Mutator {
                    param($block)
                    $block = $block.Replace("    noria:troubleTicketTrigger $($ticket.event) ;`n", "")
                    $block = $block.Replace("    dcterms:relation $($ticket.event) ;`n", "")
                    return $block
                }
            }
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "procedural"; agent = "incident_without_ticket_detector"; items = @([ordered]@{ event = "baseB:event_customer_warning" }, [ordered]@{ event = "baseB:event_workforce_warning" }) },
            @{ mode = "aposteriori"; family = "procedural"; agent = "ticket_without_linked_event_detector"; items = @([ordered]@{ ticket = "baseB:ticket_customer_warning" }, [ordered]@{ ticket = "baseB:ticket_workforce_warning" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "traceability_breakdown_diagnoser"; items = @([ordered]@{ anchor = "procedural_links_bundle_baseB"; reliability = "high"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS21_noisy_irrelevant_events"
        ReadmeTitle = "DS21 Noisy Irrelevant Events"
        Title = "Benign extra events are injected without strong diagnosis value"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "quiescentB"
        MutationType = "noise_irrelevant_events"
        Purpose = "This robustness scenario adds extra benign operational events on a resource outside the service support chains. The expected outcome is weak local noise, not a meaningful diagnosis."
        MutationNotes = @(
            "Use the quiescent healthy slice of Base B.",
            "Add three benign events on `baseB:res_firewall_02`.",
            "Keep the events far enough apart to avoid burst-style interpretations."
        )
        KpiTargets = @("noise_robustness", "ranking_stability", "sparql_efficiency_under_noise")
        InjectedAnomalies = @("baseB:event_noise_probe_01", "baseB:event_noise_probe_02", "baseB:event_noise_probe_03")
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @("Three benign events on a non-service resource")
        Notes = @(
            "The expected output is a weak functional aposteriori signal only.",
            "No level-2 diagnosis should be emitted."
        )
        Mutate = {
            param($ttl)
            $ttl = Append-Block -Ttl $ttl -Block @"
baseB:event_noise_probe_01
    a noria:EventRecord ;
    rdfs:label "Noise probe event 01"@en ;
    noria:eventRelatedElement baseB:res_firewall_02 ;
    noria:logOriginatingManagedObject baseB:res_firewall_02 ;
    noria:loggingTime "2026-03-01T08:00:00Z"^^xsd:dateTime ;
    noria:logText "Benign probe event for noise robustness."@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_noise_probe_02
    a noria:EventRecord ;
    rdfs:label "Noise probe event 02"@en ;
    noria:eventRelatedElement baseB:res_firewall_02 ;
    noria:logOriginatingManagedObject baseB:res_firewall_02 ;
    noria:loggingTime "2026-03-10T08:00:00Z"^^xsd:dateTime ;
    noria:logText "Benign probe event for noise robustness."@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_noise_probe_03
    a noria:EventRecord ;
    rdfs:label "Noise probe event 03"@en ;
    noria:eventRelatedElement baseB:res_firewall_02 ;
    noria:logOriginatingManagedObject baseB:res_firewall_02 ;
    noria:loggingTime "2026-03-20T08:00:00Z"^^xsd:dateTime ;
    noria:logText "Benign probe event for noise robustness."@en ;
    dcterms:type baseB:event_type_warning .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "functional"; agent = "resource_event_without_service_impact_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_02" }) }
        )
        L2Expectations = @()
    }
    [ordered]@{
        Id = "DS22_noisy_duplicate_and_inconsistent_records"
        ReadmeTitle = "DS22 Noisy Duplicate And Inconsistent Records"
        Title = "Weak inconsistent functional records are introduced without a decisive diagnosis"
        BaseGraph = "baseB"
        Mode = "both"
        Source = "quiescentB"
        MutationType = "noise_duplicate_inconsistent_records"
        Purpose = "This scenario introduces weakly inconsistent functional records on a low-stakes shadow chain. The purpose is to test resistance to benign inconsistency without forcing a high-level diagnosis."
        MutationNotes = @(
            "Use the quiescent healthy slice of Base B.",
            "Add a shadow module attached to two services.",
            "Add one shadow resource mapped to two applications."
        )
        KpiTargets = @("noise_robustness", "false_positive_sensitivity")
        InjectedAnomalies = @("baseB:module_shadow_ops", "baseB:res_shadow_probe")
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @("Low-stakes duplicated and inconsistent functional mappings")
        Notes = @(
            "The expected result is a few level-1 functional warnings only.",
            "No level-2 diagnoser should activate on this shadow chain."
        )
        Mutate = {
            param($ttl)
            $ttl = Append-Block -Ttl $ttl -Block @"
baseB:service_shadow_ops
    a noria:Service ;
    rdfs:label "Shadow Ops Service"@en .

baseB:app_shadow_ops
    a noria:Application ;
    rdfs:label "Shadow Ops Application"@en ;
    noria:businessCriticality baseB:criticality_medium .

baseB:module_shadow_ops
    a noria:ApplicationModule ;
    rdfs:label "Shadow Ops Module"@en ;
    seas:subSystemOf baseB:service_shadow_ops ;
    seas:subSystemOf baseB:service_network_monitoring ;
    noria:applicationModuleOf baseB:app_shadow_ops .

baseB:res_shadow_probe
    a noria:Resource ;
    rdfs:label "Shadow Probe Resource"@en ;
    noria:resourceType baseB:type_virtual_machine ;
    noria:resourceManagedBy baseB:team_platform ;
    noria:resourceForApplication baseB:app_shadow_ops ;
    noria:resourceForApplication baseB:app_monitoring_dashboard ;
    noria:locatedIn baseB:room_dc2 ;
    seas:subSystemOf baseB:zone_monitoring .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "functional"; agent = "duplicated_functional_mapping_detector"; items = @([ordered]@{ resource = "baseB:res_shadow_probe" }) },
            @{ mode = "apriori"; family = "functional"; agent = "inconsistent_service_hierarchy_detector"; items = @([ordered]@{ module = "baseB:module_shadow_ops" }) }
        )
        L2Expectations = @()
    }
    [ordered]@{
        Id = "DS23_three_diagnoses_ranked_by_urgency"
        ReadmeTitle = "DS23 Three Diagnoses Ranked By Urgency"
        Title = "Three true diagnoses coexist with different operational urgency"
        BaseGraph = "baseB"
        Mode = "aposteriori"
        Source = "baseB"
        MutationType = "ranking_three_true_diagnoses"
        Purpose = "This scenario combines a single point of failure, an unstable component, and a traceability breakdown. It is intended to evaluate ranking quality and priority calibration."
        MutationNotes = @(
            "Combine the DS11 single-point-of-failure mutation set.",
            "Combine the DS15 unstable-component mutation set.",
            "Break one additional billing ticket-event traceability link."
        )
        KpiTargets = @("top1_diagnosis_accuracy", "mrr", "priority_score_calibration")
        InjectedAnomalies = @("baseB:event_firewall_major", "baseB:ticket_firewall_major", "baseB:event_monitor_down", "baseB:event_monitor_up", "baseB:event_monitor_timeout", "baseB:event_monitor_timeout_repeat", "baseB:ticket_monitor_resolved_old", "baseB:ticket_monitor_active_new")
        RemovedEntities = @("baseB:if_workforce_vm_01", "baseB:if_firewall_01_port_02", "baseB:link_workforce_vm_01_to_firewall_01", "baseB:if_monitor_vm_01")
        RemovedRelations = @(
            "noria:troubleTicketTrigger on baseB:ticket_billing_warning",
            "dcterms:relation on baseB:ticket_billing_warning"
        )
        NoiseAdditions = @()
        RankingExpectation = @(
            "aposteriori/single_point_of_failure_diagnoser",
            "aposteriori/unstable_component_diagnoser",
            "aposteriori/traceability_breakdown_diagnoser"
        )
        Notes = @(
            "This is the main ranking benchmark for the current catalogue.",
            "The single point of failure is intended to dominate urgency."
        )
        Mutate = {
            param($ttl)
            $ttl = Ensure-BaseBStatusConcepts -Ttl $ttl
            foreach ($subject in @("baseB:if_workforce_vm_01", "baseB:if_firewall_01_port_02", "baseB:link_workforce_vm_01_to_firewall_01", "baseB:if_monitor_vm_01")) {
                $ttl = Remove-Subject -Ttl $ttl -Subject $subject
            }
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseB:ticket_billing_warning" -Mutator {
                param($block)
                $block = $block.Replace("    noria:troubleTicketTrigger baseB:event_billing_warning ;`n", "")
                $block = $block.Replace("    dcterms:relation baseB:event_billing_warning ;`n", "")
                return $block
            }
            $ttl = Append-Block -Ttl $ttl -Block @"
baseB:res_firewall_rulecard_01
    a noria:Resource ;
    rdfs:label "Firewall rule card 01"@en ;
    noria:partOf baseB:res_firewall_01 .

baseB:res_firewall_rulecard_02
    a noria:Resource ;
    rdfs:label "Firewall rule card 02"@en ;
    noria:partOf baseB:res_firewall_01 .

baseB:res_firewall_rulecard_03
    a noria:Resource ;
    rdfs:label "Firewall rule card 03"@en ;
    noria:partOf baseB:res_firewall_01 .

baseB:event_firewall_major
    a noria:EventRecord ;
    rdfs:label "Firewall major incident"@en ;
    noria:eventRelatedElement baseB:res_firewall_01 ;
    noria:logOriginatingManagedObject baseB:res_firewall_01 ;
    noria:loggingTime "2026-02-11T09:00:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_high ;
    noria:logText "Critical outage detected on firewall 01."@en ;
    dcterms:type baseB:event_type_warning .

baseB:ticket_firewall_major
    a noria:TroubleTicket ;
    rdfs:label "Firewall major incident ticket"@en ;
    noria:troubleTicketTrigger baseB:event_firewall_major ;
    dcterms:relation baseB:event_firewall_major ;
    noria:troubleTicketImpacts baseB:res_firewall_01 ;
    noria:troubleTicketRelatedResource baseB:res_firewall_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-11T09:05:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_open ;
    noria:troubleTicketSeverity baseB:severity_high ;
    noria:troubleTicketPriority baseB:priority_high ;
    noria:troubleTicketUrgency baseB:urgency_high .

baseB:event_monitor_down
    a noria:EventRecord ;
    rdfs:label "Monitoring component down"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:00:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_high ;
    noria:logText "down"@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_monitor_up
    a noria:EventRecord ;
    rdfs:label "Monitoring component up"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:02:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_minor ;
    noria:logText "up restored"@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_monitor_timeout
    a noria:EventRecord ;
    rdfs:label "Monitoring component timeout"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:03:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_minor ;
    noria:logText "timeout intermittent retry"@en ;
    dcterms:type baseB:event_type_warning .

baseB:event_monitor_timeout_repeat
    a noria:EventRecord ;
    rdfs:label "Monitoring component timeout repeat"@en ;
    noria:eventRelatedElement baseB:res_monitor_vm_01 ;
    noria:logOriginatingManagedObject baseB:res_monitor_vm_01 ;
    noria:loggingTime "2026-02-16T10:04:00Z"^^xsd:dateTime ;
    noria:alarmSeverity baseB:severity_minor ;
    noria:logText "timeout intermittent retry"@en ;
    dcterms:type baseB:event_type_warning .

baseB:ticket_monitor_resolved_old
    a noria:TroubleTicket ;
    rdfs:label "Resolved monitor incident ticket"@en ;
    noria:troubleTicketImpacts baseB:res_monitor_vm_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-15T09:30:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_resolved .

baseB:ticket_monitor_active_new
    a noria:TroubleTicket ;
    rdfs:label "Reopened monitor incident ticket"@en ;
    noria:troubleTicketImpacts baseB:res_monitor_vm_01 ;
    noria:troubleTicketDetectionDateTime "2026-02-16T10:01:00Z"^^xsd:dateTime ;
    noria:troubleTicketStatusCurrent baseB:status_open ;
    noria:troubleTicketSeverity baseB:severity_high ;
    noria:troubleTicketPriority baseB:priority_high ;
    noria:troubleTicketUrgency baseB:urgency_high .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "aposteriori"; family = "structural"; agent = "isolated_incident_resource_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_01" }) },
            @{ mode = "aposteriori"; family = "structural"; agent = "incident_on_incomplete_link_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_01" }) },
            @{ mode = "aposteriori"; family = "structural"; agent = "no_redundancy_incident_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_01" }) },
            @{ mode = "aposteriori"; family = "structural"; agent = "high_impact_resource_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_01" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "event_burst_detector"; items = @([ordered]@{ element = "baseB:res_monitor_vm_01" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "flapping_state_detector"; items = @([ordered]@{ element = "baseB:res_monitor_vm_01" }) },
            @{ mode = "aposteriori"; family = "dynamic"; agent = "reopened_incident_detector"; items = @([ordered]@{ relatedElement = "baseB:res_monitor_vm_01" }) },
            @{ mode = "aposteriori"; family = "procedural"; agent = "incident_without_ticket_detector"; items = @([ordered]@{ event = "baseB:event_billing_warning" }) },
            @{ mode = "aposteriori"; family = "procedural"; agent = "ticket_without_linked_event_detector"; items = @([ordered]@{ ticket = "baseB:ticket_billing_warning" }) }
        )
        L2Expectations = @(
            @{ mode = "aposteriori"; agent = "single_point_of_failure_diagnoser"; items = @([ordered]@{ anchor = "baseB:res_firewall_01"; reliability = "high"; severity = "high" }) },
            @{ mode = "aposteriori"; agent = "unstable_component_diagnoser"; items = @([ordered]@{ anchor = "baseB:res_monitor_vm_01"; reliability = "high"; severity = "medium" }) },
            @{ mode = "aposteriori"; agent = "traceability_breakdown_diagnoser"; items = @([ordered]@{ anchor = "baseB:app_billing_gateway"; reliability = "medium"; severity = "medium" }) }
        )
    }
    [ordered]@{
        Id = "DS24_reliability_calibration_bundle"
        ReadmeTitle = "DS24 Reliability Calibration Bundle"
        Title = "Several diagnosis candidates are present with different evidence strengths"
        BaseGraph = "baseB"
        Mode = "both"
        Source = "quiescentB"
        MutationType = "reliability_calibration_bundle"
        Purpose = "This scenario deliberately mixes a weak observability gap, a medium critical service exposure, and a strong structural fragility case. It is intended for reliability-calibration experiments."
        MutationNotes = @(
            "Add one event without related element and remove one change actual end time.",
            "Reduce the customer portal support chain to one resource.",
            "Create a strongly fragile firewall resource by removing its interfaces, parent, and management."
        )
        KpiTargets = @("reliability_score_calibration", "activation_threshold_sanity")
        InjectedAnomalies = @("baseB:event_reliability_gap")
        RemovedEntities = @("baseB:if_firewall_02_port_01", "baseB:if_firewall_02_port_02")
        RemovedRelations = @(
            "noria:changeRequestActualEndTime on baseB:change_switch_maintenance",
            "noria:resourceForApplication on baseB:res_customer_vm_02",
            "noria:resourceManagedBy on baseB:res_firewall_02",
            "seas:subSystemOf on baseB:res_firewall_02"
        )
        NoiseAdditions = @()
        RankingExpectation = @(
            "apriori/structural_fragility_diagnoser",
            "apriori/critical_service_exposure_diagnoser",
            "apriori/observability_gap_diagnoser"
        )
        Notes = @(
            "This scenario is not about urgency but about evidence strength.",
            "The structural fragility case is intended to have the strongest support."
        )
        Mutate = {
            param($ttl)
            foreach ($subject in @("baseB:if_firewall_02_port_01", "baseB:if_firewall_02_port_02")) {
                $ttl = Remove-Subject -Ttl $ttl -Subject $subject
            }
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseB:change_switch_maintenance" -Mutator {
                param($block)
                return ($block -replace "\n\s*noria:changeRequestActualEndTime .*?\.", "")
            }
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseB:res_customer_vm_02" -Mutator {
                param($block)
                return $block.Replace("    noria:resourceForApplication baseB:app_customer_portal ;`n", "")
            }
            $ttl = Update-SubjectBlock -Ttl $ttl -Subject "baseB:res_firewall_02" -Mutator {
                param($block)
                $block = $block.Replace("    noria:resourceManagedBy baseB:team_network ;`n", "")
                $block = $block.Replace("    seas:subSystemOf baseB:zone_network .", ".")
                return $block
            }
            $ttl = Append-Block -Ttl $ttl -Block @"
baseB:event_reliability_gap
    a noria:EventRecord ;
    rdfs:label "Reliability gap event without related element"@en ;
    noria:loggingTime "2026-03-03T08:00:00Z"^^xsd:dateTime ;
    noria:logText "Weak observability issue for calibration."@en ;
    dcterms:type baseB:event_type_warning .
"@
            return $ttl
        }
        L1Expectations = @(
            @{ mode = "apriori"; family = "dynamic"; agent = "change_without_effective_time_detector"; items = @([ordered]@{ change = "baseB:change_switch_maintenance" }) },
            @{ mode = "apriori"; family = "dynamic"; agent = "event_without_related_element_detector"; items = @([ordered]@{ event = "baseB:event_reliability_gap" }) },
            @{ mode = "apriori"; family = "structural"; agent = "missing_redundancy_detector"; items = @([ordered]@{ application = "baseB:app_customer_portal" }) },
            @{ mode = "apriori"; family = "structural"; agent = "criticality_structural_weakness_detector"; items = @([ordered]@{ application = "baseB:app_customer_portal" }) },
            @{ mode = "apriori"; family = "functional"; agent = "over_concentrated_service_detector"; items = @([ordered]@{ service = "baseB:service_customer_access" }) },
            @{ mode = "apriori"; family = "structural"; agent = "missing_interface_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_02" }) },
            @{ mode = "apriori"; family = "structural"; agent = "missing_parent_resource_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_02" }) },
            @{ mode = "apriori"; family = "structural"; agent = "unmanaged_resource_detector"; items = @([ordered]@{ resource = "baseB:res_firewall_02" }) }
        )
        L2Expectations = @(
            @{ mode = "apriori"; agent = "observability_gap_diagnoser"; items = @([ordered]@{ anchor = "baseB:event_reliability_gap"; reliability = "low"; severity = "low" }) },
            @{ mode = "apriori"; agent = "critical_service_exposure_diagnoser"; items = @([ordered]@{ anchor = "baseB:app_customer_portal"; reliability = "medium"; severity = "medium" }) },
            @{ mode = "apriori"; agent = "structural_fragility_diagnoser"; items = @([ordered]@{ anchor = "baseB:res_firewall_02"; reliability = "high"; severity = "high" }) }
        )
    }
    [ordered]@{
        Id = "DS25_scalability_small"
        ReadmeTitle = "DS25 Scalability Small"
        Title = "Small clean graph for the first point of the scalability curve"
        BaseGraph = "baseA"
        Mode = "both"
        Source = "quiescentA"
        MutationType = "scalability_small"
        Purpose = "This scenario is the small clean graph used as the first point of the scalability curve."
        MutationNotes = @(
            "Reuse the quiescent healthy slice of Base A.",
            "Do not inject any anomaly."
        )
        KpiTargets = @("end_to_end_runtime", "mean_runtime_per_detector", "mean_runtime_per_diagnoser", "sparql_efficiency", "scalability_curve_point_1")
        InjectedAnomalies = @()
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "This scenario should stay silent at both level 1 and level 2.",
            "It is the smallest runtime baseline in the catalogue."
        )
        Mutate = { param($ttl) return $ttl }
        L1Expectations = @()
        L2Expectations = @()
    }
    [ordered]@{
        Id = "DS26_scalability_medium"
        ReadmeTitle = "DS26 Scalability Medium"
        Title = "Medium clean graph for the second point of the scalability curve"
        BaseGraph = "baseB"
        Mode = "both"
        Source = "quiescentB"
        MutationType = "scalability_medium"
        Purpose = "This scenario is the medium clean graph used as the second point of the scalability curve."
        MutationNotes = @(
            "Reuse the quiescent healthy slice of Base B.",
            "Do not inject any anomaly."
        )
        KpiTargets = @("end_to_end_runtime", "mean_runtime_per_detector", "mean_runtime_per_diagnoser", "sparql_efficiency", "scalability_curve_point_2")
        InjectedAnomalies = @()
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @()
        Notes = @(
            "This scenario should stay silent at both level 1 and level 2.",
            "It is larger than DS25 but semantically equivalent."
        )
        Mutate = { param($ttl) return $ttl }
        L1Expectations = @()
        L2Expectations = @()
    }
    [ordered]@{
        Id = "DS27_scalability_large"
        ReadmeTitle = "DS27 Scalability Large"
        Title = "Large clean graph for the third point of the scalability curve"
        BaseGraph = "baseB"
        Mode = "both"
        Source = "largeQuiescentB"
        MutationType = "scalability_large"
        Purpose = "This scenario is the large clean graph used as the third point of the scalability curve."
        MutationNotes = @(
            "Start from the quiescent healthy slice of Base B.",
            "Append two additional healthy service/application/resource stacks.",
            "Do not inject any anomaly."
        )
        KpiTargets = @("end_to_end_runtime", "mean_runtime_per_detector", "mean_runtime_per_diagnoser", "sparql_efficiency", "scalability_curve_point_3")
        InjectedAnomalies = @()
        RemovedEntities = @()
        RemovedRelations = @()
        NoiseAdditions = @("Two extra healthy business stacks")
        Notes = @(
            "This is the largest clean runtime baseline in the catalogue.",
            "It stays semantically healthy while increasing graph size."
        )
        Mutate = { param($ttl) return $ttl }
        L1Expectations = @()
        L2Expectations = @()
    }
)

function Get-SourceText {
    param([string]$Source)

    switch ($Source) {
        "baseA" { return $baseAText }
        "baseB" { return $baseBText }
        "quiescentA" { return $quiescentBaseAText }
        "quiescentB" { return Get-QuiescentBaseB }
        "largeQuiescentB" { return Get-LargeQuiescentBaseB }
        default { throw "Unknown source text key: $Source" }
    }
}

foreach ($scenario in $scenarios) {
    $scenarioDir = Join-Path $datasetsRoot $scenario.Id
    New-Item -ItemType Directory -Path $scenarioDir -Force | Out-Null

    $ttl = Get-SourceText -Source $scenario.Source
    $ttl = & $scenario.Mutate $ttl
    $ttl = Normalize-Text $ttl

    $level1 = New-EmptyLevel1 -L1Detectors $L1Detectors
    $level2 = New-EmptyLevel2 -L2Diagnosers $L2Diagnosers
    Apply-L1Expectations -Target $level1 -Expectations $scenario.L1Expectations
    Apply-L2Expectations -Target $level2 -Expectations $scenario.L2Expectations

    $nonZeroL1 = Get-NonZeroLevel1Agents -Level1 $level1
    $nonZeroL2 = Get-NonZeroLevel2Diagnosers -Level2 $level2

    $manifest = [ordered]@{
        dataset_id = $scenario.Id
        title = $scenario.Title
        base_graph = $scenario.BaseGraph
        source_variant = $scenario.Source
        mode = $scenario.Mode
        graph_files = @("dataset.ttl")
        mutation_profile = [ordered]@{
            type = $scenario.MutationType
            injected_anomalies = $scenario.InjectedAnomalies
            removed_entities = $scenario.RemovedEntities
            removed_relations = $scenario.RemovedRelations
            noise_additions = $scenario.NoiseAdditions
        }
        kpi_targets = $scenario.KpiTargets
        expected_summary = [ordered]@{
            nonzero_level1_agents = $nonZeroL1
            nonzero_level2_diagnosers = $nonZeroL2
            level1_total_bindings = (Get-Level1BindingCount -Level1 $level1)
            level2_total_diagnoses = (Get-Level2DiagnosisCount -Level2 $level2)
        }
    }

    if ($scenario.Keys -contains "RankingExpectation") {
        $manifest["ranking_expectation"] = $scenario.RankingExpectation
    }

    $readme = Build-ScenarioReadme -Scenario $scenario -Level1 $level1 -Level2 $level2 -NonZeroL1 $nonZeroL1 -NonZeroL2 $nonZeroL2

    Write-Utf8File -Path (Join-Path $scenarioDir "dataset.ttl") -Content $ttl
    Write-Utf8File -Path (Join-Path $scenarioDir "README.md") -Content $readme
    Write-JsonFile -Path (Join-Path $scenarioDir "manifest.json") -Data $manifest
    Write-JsonFile -Path (Join-Path $scenarioDir "expected_level1.json") -Data $level1
    Write-JsonFile -Path (Join-Path $scenarioDir "expected_level2.json") -Data $level2
}
