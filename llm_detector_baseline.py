"""
llm_detector_baseline.py

Baseline comparison: LLM-as-detector vs MAS.

Gives the full NORIA-O knowledge graph to a local LLM (mistral:latest via
Ollama) and asks it to detect network anomalies — without any MAS pre-
processing. Two prompt strategies:

  guided  — briefs the LLM on the ontology, entity types, and the diagnostic
             task, without naming specific anomaly patterns (like a manager
             briefing a new analyst)
  open    — minimal context, free-form detection

Results are compared against the MAS ground truth (results/ directory).

Metrics:
  recall            fraction of MAS-detected entities the LLM also found
  precision         fraction of LLM-detected entities confirmed by MAS
  hallucination     fraction of LLM detections referencing non-existent entities

Also exports the graph as noria_graph.ttl for manual use in Claude/GPT chat.

Usage:
    python -X utf8 llm_detector_baseline.py [apriori|aposteriori|both] [guided|open|both]

Output:
    llm_baseline_results.json
    noria_graph.ttl
"""

import json
import re
import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT    = Path(__file__).resolve().parent
SPARQL_ENDPOINT = "http://localhost:8890/sparql"
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL           = "mistral:latest"
RESULTS_DIR     = PROJECT_ROOT / "results"

# ─────────────────────────────────────────────────────────────────────────────
# GRAPH EXPORT  (diagnostic predicates only — strips prov/foaf/label noise)
# ─────────────────────────────────────────────────────────────────────────────

# Only keep predicates that carry diagnostic information.
# Eliminates: prov:wasDerivedFrom (×96), foaf:* (×45), rdfs:label (×24),
#             resourceHostName/LogisticId/ProductModel (×32), org:memberOf (×9)
GRAPH_QUERY = """
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX noria: <https://w3id.org/noria/ontology/>
PREFIX seas:  <https://w3id.org/seas/>
PREFIX dct:   <http://purl.org/dc/terms/>
PREFIX pep:   <https://w3id.org/pep/>

CONSTRUCT { ?s ?p ?o }
WHERE {
  ?s ?p ?o .
  FILTER(STRSTARTS(STR(?s), 'https://w3id.org/noria/'))
  FILTER(?p IN (
    rdf:type,
    noria:networkInterfaceOf,
    noria:networkInterfaceConnects,
    noria:networkLinkTerminationResource,
    noria:resourceForApplication,
    noria:applicationModuleOf,
    noria:applicationShortIdentifier,
    noria:applicationType,
    noria:businessCriticality,
    seas:subSystemOf,
    noria:resourceManagedBy,
    noria:resourceType,
    noria:partOf,
    noria:locatedIn,
    dct:relation,
    noria:logOriginatingManagedObject,
    noria:logOriginatingManagementSystem,
    noria:troubleTicketRelatedResource,
    noria:troubleTicketStatusCurrent,
    noria:troubleTicketDetectionDateTime,
    noria:alarmPerceivedSeverity,
    noria:alarmProposedRepairAction,
    noria:conformsTo,
    noria:loggingTime,
    dct:type,
    dct:description,
    dct:created,
    noria:documentStatusHistory,
    noria:hasPart,
    noria:alarmSeverity,
    noria:changeRequestActualStartTime,
    noria:changeRequestActualEndTime,
    noria:plannedStartDate,
    noria:plannedEndDate,
    noria:changeStatus
  ))
}
"""

def export_graph_turtle() -> str:
    r = requests.get(
        SPARQL_ENDPOINT,
        params={"query": GRAPH_QUERY, "format": "text/turtle"},
        timeout=30,
    )
    r.raise_for_status()
    return r.text


def extract_graph_entity_names(graph_turtle: str) -> set[str]:
    """Return the set of local names of all entities present in the graph."""
    names: set[str] = set()
    # Full URIs in angle brackets
    for uri in re.findall(r'<(https?://[^>]+)>', graph_turtle):
        local = uri.rstrip("/").split("/")[-1].split("#")[-1]
        if local:
            names.add(local)
    # Prefixed names (ns1:RES_TOY_as2, noria:Resource, etc.)
    for local in re.findall(r'(?:[\w]+:)([\w][\w\d_.%-]+)', graph_turtle):
        names.add(local)
    return names


# ─────────────────────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

_ONTOLOGY_BRIEFING = """\
You are a network operations expert analyzing a knowledge graph that models an \
ICT/telecom infrastructure using the NORIA-O ontology.

The graph uses these main entity types:
  noria:Resource             physical or virtual network element (router, server, rack…)
  noria:NetworkInterface     network interface card attached to a resource
  noria:NetworkLink          cable or logical link connecting two interfaces
  noria:Application          software application running on one or more resources
  noria:ApplicationModule    functional module within an application
  noria:Service              business-facing service exposed by the application layer
  noria:TroubleTicket        incident ticket opened by the operations team
  noria:EventRecord          log entry, alarm, or state change emitted by the network
  noria:ChangeRequest        planned maintenance or configuration change
  pep:Procedure              operational procedure associated with a repair action

Key relationships:
  noria:networkInterfaceOf            interface → resource it belongs to
  noria:networkInterfaceConnects      interface → network link it connects to
  noria:networkLinkTerminationResource  link → its endpoint resources
  noria:resourceForApplication        resource → application it supports
  noria:applicationModuleOf           module → parent application
  seas:subSystemOf                    hierarchy (module→service, resource→rack…)
  noria:resourceManagedBy             resource → responsible team
  noria:partOf                        physical containment
  noria:locatedIn                     geographic location
  dct:relation                        ticket/change → related event records
  noria:logOriginatingManagedObject   event → affected resource
  noria:logOriginatingManagementSystem  event → originating management application
  noria:troubleTicketRelatedResource  ticket → impacted resource
  noria:alarmPerceivedSeverity        event severity (major, minor, critical…)
  noria:alarmProposedRepairAction     event → suggested repair procedure
  noria:businessCriticality           application criticality level\
"""

_OUTPUT_FORMAT = """\
Return ONLY a JSON array. Each entry must follow this schema exactly:
[
  {
    "anomaly_type": "<short descriptive label>",
    "entity":       "<full URI of the primary affected entity>",
    "family":       "structural|dynamic|functional|procedural",
    "explanation":  "<one sentence>",
    "severity":     "LOW|MEDIUM|HIGH|CRITICAL"
  }
]
If you find no anomaly, return an empty array []. No other text.\
"""

def build_prompt_guided(graph_turtle: str, mode: str) -> str:
    if mode == "apriori":
        task = """\
Task: review the CONFIGURATION of this network (ignore incident and event data) \
and identify all structural weaknesses, topology problems, and governance gaps \
that make this network fragile or hard to operate.

Think about:
  - Are all entities properly connected and integrated into the topology?
  - Do applications and services have adequate technical support?
  - Are there entities that appear isolated, incomplete, or inconsistently linked?
  - Does every critical component have appropriate redundancy and management?\
"""
    else:
        task = """\
Task: given the INCIDENTS and EVENTS already recorded in this graph, diagnose \
what went wrong and identify all anomalies that explain or aggravate the \
observed failures.

Think about:
  - Which resources, applications, and services are involved in the incidents?
  - What structural or functional weaknesses made these incidents possible or \
harder to resolve?
  - Is there evidence of propagation, cascading failure, or a single point of failure?
  - Is the operational traceability intact (events linked to tickets, \
tickets linked to procedures)?\
"""

    return f"""{_ONTOLOGY_BRIEFING}

Knowledge graph (Turtle):

```turtle
{graph_turtle}
```

{task}

{_OUTPUT_FORMAT}"""


def build_prompt_open(graph_turtle: str, mode: str) -> str:
    mode_hint = (
        "Focus on the static network configuration, not on incidents."
        if mode == "apriori"
        else "Focus on diagnosing the observed incidents and their root causes."
    )
    return f"""\
You are a network analyst. Below is a knowledge graph of an ICT network \
in Turtle format. {mode_hint}

Identify every anomaly, weakness, or problem you can detect.

```turtle
{graph_turtle}
```

{_OUTPUT_FORMAT}"""


# ─────────────────────────────────────────────────────────────────────────────
# LLM CALL
# ─────────────────────────────────────────────────────────────────────────────

def call_llm(prompt: str) -> str:
    # num_ctx must cover the full prompt; 16384 fits our ~9k-token graphs.
    # Timeout is 30 min per call — CPU inference on a large context is slow.
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True,          # stream for progress visibility
        "options": {
            "temperature": 0.1,
            "num_ctx": 16384,
        },
    }
    r = requests.post(OLLAMA_ENDPOINT, json=payload, stream=True, timeout=3600)
    r.raise_for_status()

    chunks: list[str] = []
    chars_printed = 0
    for line in r.iter_lines():
        if not line:
            continue
        data = json.loads(line)
        token = data.get("response", "")
        chunks.append(token)
        chars_printed += len(token)
        if chars_printed % 200 < len(token):   # progress dot every ~200 chars
            print(".", end="", flush=True)
        if data.get("done"):
            break
    print()
    return "".join(chunks)


def parse_detections(response: str) -> list[dict]:
    # Try to extract JSON array from response
    match = re.search(r'\[[\s\S]*\]', response)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        return []


# ─────────────────────────────────────────────────────────────────────────────
# MAS GROUND TRUTH
# ─────────────────────────────────────────────────────────────────────────────

def load_mas_entities(mode: str) -> dict[str, set[str]]:
    """
    Load MAS results for a given mode.
    Returns {agent_stem: {local_entity_name, ...}}.
    """
    mas: dict[str, set[str]] = {}
    for family_dir in sorted(RESULTS_DIR.iterdir()):
        if not family_dir.is_dir() or family_dir.name == "level2":
            continue
        mode_dir = family_dir / mode
        if not mode_dir.exists():
            continue
        for f in sorted(mode_dir.glob("*.json")):
            raw = json.loads(f.read_text(encoding="utf-8"))
            entities: set[str] = set()
            for item in raw if isinstance(raw, list) else []:
                if not isinstance(item, dict):
                    continue
                for v in item.values():
                    if isinstance(v, dict) and v.get("type") == "uri":
                        uri = v["value"]
                        local = uri.rstrip("/").split("/")[-1]
                        entities.add(local)
                        entities.add(uri)
            if entities:
                mas[f.stem] = entities
    return mas


# ─────────────────────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_metrics(
    detections: list[dict],
    mas_entities: dict[str, set[str]],
    graph_names: set[str],
) -> dict:
    # Flat set of all MAS-detected local names
    mas_flat: set[str] = set()
    for entities in mas_entities.values():
        for e in entities:
            mas_flat.add(e.rstrip("/").split("/")[-1])

    # LLM detected local names + full URIs
    llm_locals: set[str] = set()
    hallucinated: list[str] = []
    for det in detections:
        entity = det.get("entity", "")
        # Handle full URIs, Turtle prefixed names (ns3:RES_TOY_as2 → RES_TOY_as2)
        local = entity.rstrip("/").split("/")[-1].split("#")[-1]
        if ":" in local:
            local = local.split(":")[-1]
        if local:
            llm_locals.add(local)
        # Hallucination: local name not present anywhere in the graph
        if entity and local not in graph_names and entity not in graph_names:
            hallucinated.append(entity)

    matched = llm_locals & mas_flat

    recall    = len(matched) / len(mas_flat)       if mas_flat    else 1.0
    precision = len(matched) / len(llm_locals)     if llm_locals  else 0.0
    hall_rate = len(hallucinated) / len(detections) if detections  else 0.0

    # Per-agent recall
    per_agent: dict[str, bool] = {}
    for agent, entities in mas_entities.items():
        agent_locals = {e.rstrip("/").split("/")[-1] for e in entities}
        per_agent[agent] = bool(agent_locals & llm_locals)

    return {
        "n_llm_detections":   len(detections),
        "n_mas_entities":     len(mas_flat),
        "recall":             round(recall, 3),
        "precision":          round(precision, 3),
        "hallucination_rate": round(hall_rate, 3),
        "agents_covered":     sum(per_agent.values()),
        "agents_total":       len(per_agent),
        "agent_recall":       round(sum(per_agent.values()) / len(per_agent), 3) if per_agent else 0.0,
        "per_agent_hit":      {k: v for k, v in sorted(per_agent.items())},
        "found_entities":     sorted(matched),
        "missed_entities":    sorted(mas_flat - llm_locals),
        "hallucinated":       hallucinated[:20],
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def run_one(mode: str, strategy: str, graph_turtle: str, graph_names: set[str] | None = None) -> dict:
    print(f"\n  [{mode.upper()} / {strategy.upper()}]")

    if strategy == "guided":
        prompt = build_prompt_guided(graph_turtle, mode)
    else:
        prompt = build_prompt_open(graph_turtle, mode)

    token_est = len(prompt) // 4
    print(f"  Prompt ~{token_est:,} tokens — calling {MODEL}...")

    t0 = time.perf_counter()
    try:
        response = call_llm(prompt)
    except requests.exceptions.Timeout:
        print("  TIMEOUT after 600s")
        return {"error": "timeout"}
    except Exception as exc:
        print(f"  ERROR: {exc}")
        return {"error": str(exc)}
    elapsed = round(time.perf_counter() - t0, 1)

    detections = parse_detections(response)
    print(f"  {len(detections)} detections in {elapsed}s")

    mas_entities  = load_mas_entities(mode)
    if graph_names is None:
        graph_names = extract_graph_entity_names(graph_turtle)
    metrics       = compute_metrics(detections, mas_entities, graph_names)

    print(
        f"  recall={metrics['recall']:.2f}  "
        f"precision={metrics['precision']:.2f}  "
        f"halluc={metrics['hallucination_rate']:.2f}  "
        f"agents hit={metrics['agents_covered']}/{metrics['agents_total']}"
    )

    return {
        "mode":            mode,
        "strategy":        strategy,
        "model":           MODEL,
        "elapsed_s":       elapsed,
        "prompt_tokens":   token_est,
        "raw_response":    response,
        "detections":      detections,
        "metrics":         metrics,
    }


def main() -> None:
    mode_arg     = sys.argv[1] if len(sys.argv) > 1 else "both"
    strategy_arg = sys.argv[2] if len(sys.argv) > 2 else "both"

    modes      = ["apriori", "aposteriori"] if mode_arg     == "both" else [mode_arg]
    strategies = ["guided",  "open"]        if strategy_arg == "both" else [strategy_arg]

    print("=" * 60)
    print(f"  LLM DETECTOR BASELINE  ({MODEL})")
    print("=" * 60)

    print("\n  Exporting knowledge graph from Virtuoso...")
    try:
        graph_turtle = export_graph_turtle()
    except Exception as exc:
        print(f"  ERROR: {exc}")
        sys.exit(1)

    token_est = len(graph_turtle) // 4
    print(f"  {len(graph_turtle):,} chars  (~{token_est:,} tokens)")

    # Save .ttl for manual use in Claude/GPT chat
    ttl_path = PROJECT_ROOT / "noria_graph.ttl"
    ttl_path.write_text(graph_turtle, encoding="utf-8")
    print(f"  Graph saved to {ttl_path.name}  (attach to Claude/GPT chat for manual tests)")

    # Load any previously completed results so reruns can skip finished combos
    out = PROJECT_ROOT / "llm_baseline_results.json"
    results: dict = {}
    if out.exists():
        try:
            results = json.loads(out.read_text(encoding="utf-8"))
        except Exception:
            results = {}

    graph_names = extract_graph_entity_names(graph_turtle)

    for mode in modes:
        results.setdefault(mode, {})
        for strategy in strategies:
            existing = results[mode].get(strategy)
            if existing and "error" not in existing:
                # Always recompute metrics from stored detections so a fix to
                # compute_metrics is reflected without re-running the LLM.
                mas_entities = load_mas_entities(mode)
                existing["metrics"] = compute_metrics(
                    existing.get("detections", []), mas_entities, graph_names
                )
                results[mode][strategy] = existing
                m = existing["metrics"]
                print(f"\n  [{mode.upper()} / {strategy.upper()}]  skipped (already done, metrics refreshed)")
                print(
                    f"  recall={m['recall']:.2f}  precision={m['precision']:.2f}  "
                    f"halluc={m['hallucination_rate']:.2f}  "
                    f"agents hit={m['agents_covered']}/{m['agents_total']}"
                )
                out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
                continue
            results[mode][strategy] = run_one(mode, strategy, graph_turtle, graph_names)
            # Save after each combo so a crash doesn't lose work
            out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    header = f"  {'Mode':<14} {'Strategy':<8} {'Det.':>5} {'Recall':>8} {'Prec.':>8} {'Hall.':>7} {'Agents':>8} {'Time':>7}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for mode in modes:
        for strategy in strategies:
            r = results[mode][strategy]
            if "error" in r:
                print(f"  {mode:<14} {strategy:<8}  ERROR: {r['error']}")
                continue
            m = r["metrics"]
            print(
                f"  {mode:<14} {strategy:<8} "
                f"{m['n_llm_detections']:>5} "
                f"{m['recall']:>8.2f} "
                f"{m['precision']:>8.2f} "
                f"{m['hallucination_rate']:>7.2f} "
                f"{m['agents_covered']:>3}/{m['agents_total']:<3} "
                f"{r['elapsed_s']:>6.0f}s"
            )

    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Full results saved to {out.name}")


if __name__ == "__main__":
    main()
