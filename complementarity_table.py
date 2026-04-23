"""
complementarity_table.py

Reads all level-1 result JSON files produced by run_all_detectors.py and builds
a complementarity table showing which anomaly families detect which entity types,
and which entities are detected by multiple families simultaneously (synergy cases).

Output:
  - prints the table to stdout
  - saves complementarity_results.json
"""

import json
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_ROOT = PROJECT_ROOT / "results"

FAMILIES = ["structural", "dynamic", "functional", "procedural"]
MODES    = ["apriori", "aposteriori"]

# Entity keys used by each family in SPARQL results
ENTITY_KEYS = ["resource", "application", "service", "module",
                "change", "ticket", "event", "interface", "link"]


def short(uri: str) -> str:
    return uri.split("/")[-1].split("#")[-1]


def load_results() -> dict:
    """
    Returns {family: {mode: {agent_name: [list of entity URIs detected]}}}
    """
    data = defaultdict(lambda: defaultdict(dict))

    for family in FAMILIES:
        for mode in MODES:
            folder = RESULTS_ROOT / family / mode
            if not folder.exists():
                continue
            for json_file in sorted(folder.glob("*.json")):
                agent = json_file.stem.replace("_results", "")
                try:
                    rows = json.loads(json_file.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if not rows:
                    continue
                # collect all entity URIs from any known key
                entities = set()
                for row in rows:
                    for key in ENTITY_KEYS:
                        if key in row:
                            entities.add(row[key]["value"])
                if entities:
                    data[family][mode][agent] = list(entities)

    return data


def build_agent_table(data: dict, mode: str) -> None:
    """Table 1: one row per active agent, columns = family."""
    print(f"\n  ACTIVE AGENTS — {mode.upper()} MODE")
    print(f"  {'Agent':<52} {'Family':<12} {'Detections':>10}")
    print("  " + "-" * 78)

    rows = []
    for family in FAMILIES:
        for agent, entities in data[family].get(mode, {}).items():
            rows.append((family, agent, len(entities)))

    rows.sort(key=lambda x: (-x[2], x[0]))
    for family, agent, n in rows:
        print(f"  {agent:<52} {family:<12} {n:>10}")

    total_agents  = len(rows)
    total_detects = sum(r[2] for r in rows)
    print(f"\n  {total_agents} active agents, {total_detects} total detections")


def build_family_coverage(data: dict, mode: str) -> None:
    """Table 2: for each family, count agents with results vs total."""
    print(f"\n  FAMILY COVERAGE — {mode.upper()} MODE")
    print(f"  {'Family':<14} {'Active agents':>14} {'Total detections':>17}")
    print("  " + "-" * 48)

    for family in FAMILIES:
        agents   = data[family].get(mode, {})
        n_active = len(agents)
        n_total  = sum(len(e) for e in agents.values())
        bar      = "#" * min(n_total, 30)
        print(f"  {family:<14} {n_active:>14} {n_total:>17}  {bar}")


def build_synergy_table(data: dict, mode: str) -> list:
    """
    Table 3: entities detected by 2+ families simultaneously.
    These are the cases level-2 agents can correlate.
    """
    # Collect all entities per family
    family_entities = {}
    for family in FAMILIES:
        entities = set()
        for agent_entities in data[family].get(mode, {}).values():
            entities.update(agent_entities)
        family_entities[family] = entities

    # Find entities in 2+ families
    all_entities = set()
    for entities in family_entities.values():
        all_entities.update(entities)

    synergy = []
    for uri in sorted(all_entities):
        families_present = [f for f in FAMILIES if uri in family_entities[f]]
        if len(families_present) >= 2:
            synergy.append((short(uri), families_present, uri))

    if not synergy:
        print(f"\n  SYNERGY CASES — {mode.upper()}: none (no entity detected by 2+ families)")
        return []

    print(f"\n  SYNERGY CASES — {mode.upper()} MODE")
    print(f"  (entities detected by 2 or more families — level-2 correlation targets)")
    print(f"  {'Entity':<40} Structural  Dynamic  Functional  Procedural")
    print("  " + "-" * 80)

    for name, families, uri in synergy:
        cols = {f: "   ✓   " if f in families else "       " for f in FAMILIES}
        print(f"  {name:<40} {cols['structural']}  {cols['dynamic']}   {cols['functional']}   {cols['procedural']}")

    print(f"\n  {len(synergy)} synergy case(s) identified")
    return synergy


def build_non_redundancy_proof(data: dict) -> None:
    """
    Shows that each family detects things no other family detects.
    If every family has at least one unique detection, they are non-redundant.
    """
    print(f"\n  NON-REDUNDANCY PROOF")
    print(f"  (anomaly types detectable ONLY by one specific family)")
    print(f"  {'Family':<14} {'Unique agent':<50} {'Example detections':>5}")
    print("  " + "-" * 72)

    for mode in MODES:
        family_entities = {}
        for family in FAMILIES:
            entities = set()
            for agent_entities in data[family].get(mode, {}).values():
                entities.update(agent_entities)
            family_entities[family] = entities

        for family in FAMILIES:
            own  = family_entities[family]
            rest = set()
            for f2 in FAMILIES:
                if f2 != family:
                    rest.update(family_entities[f2])
            unique = own - rest
            agents = list(data[family].get(mode, {}).keys())
            agent_str = agents[0] if agents else "-"
            marker = "UNIQUE" if unique else "overlap"
            print(f"  {family:<14} [{mode:>11}]  {agent_str:<36}  {len(unique):>3} unique  {marker}")


def main():
    print("=" * 60)
    print("  COMPLEMENTARITY TABLE")
    print("=" * 60)

    data = load_results()

    if not any(data[f] for f in FAMILIES):
        print("\n  No results found. Run run_all_detectors.py first.")
        return

    results_summary = {}

    for mode in MODES:
        has_data = any(data[f].get(mode) for f in FAMILIES)
        if not has_data:
            continue
        build_agent_table(data, mode)
        build_family_coverage(data, mode)
        synergy = build_synergy_table(data, mode)
        results_summary[mode] = {
            "families": {
                f: {
                    "active_agents": list(data[f].get(mode, {}).keys()),
                    "total_detections": sum(len(e) for e in data[f].get(mode, {}).values()),
                }
                for f in FAMILIES
            },
            "synergy_cases": [
                {"entity": name, "families": families}
                for name, families, _ in synergy
            ],
        }

    build_non_redundancy_proof(data)

    out = PROJECT_ROOT / "complementarity_results.json"
    out.write_text(json.dumps(results_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Full results saved to {out.name}")


if __name__ == "__main__":
    main()
