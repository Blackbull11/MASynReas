import requests, json, sys

ENDPOINT   = "http://localhost:8890/sparql"
OUTPUT_FILE = "result_propagation.json"

QUERY = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX noria:   <https://w3id.org/noria/ontology/>

SELECT ?faultyResource ?neighborResource ?linkId ?neighborLog
WHERE {
  ?tt a noria:TroubleTicket .
  ?tt dcterms:relation ?log .
  ?log noria:alarmPerceivedSeverity
       <https://w3id.org/noria/kos/Notification/Severity/PerceivedSeverity/major> .
  ?log noria:logOriginatingManagedObject ?faultyResource .

  ?link a noria:NetworkLink .
  ?link noria:networkLinkId ?linkId .
  ?link noria:networkLinkTerminationResource ?faultyResource .
  ?link noria:networkLinkTerminationResource ?neighborResource .
  FILTER(?neighborResource != ?faultyResource)

  ?tt dcterms:relation ?neighborEvent .
  ?neighborEvent noria:logOriginatingManagedObject ?neighborResource .
  ?neighborEvent noria:logText ?neighborLog .
}
"""

def local_name(uri): return uri.split("/")[-1]

def run():
    print("[Python] Agent2: querying network propagation...")
    r = requests.get(ENDPOINT,
                     headers={"Accept": "application/sparql-results+json"},
                     params={"query": QUERY, "format": "application/sparql-results+json"},
                     timeout=30)
    r.raise_for_status()
    bindings = r.json()["results"]["bindings"]
    print(f"[Python] Agent2: {len(bindings)} propagation(s) found.")

    # Group by faulty resource
    propagation = {}
    for b in bindings:
        src  = local_name(b["faultyResource"]["value"])
        dst  = local_name(b["neighborResource"]["value"])
        link = b["linkId"]["value"]
        log  = b["neighborLog"]["value"]
        if src not in propagation:
            propagation[src] = {"faulty_resource": src, "link": link, "impacted": []}
        if dst not in [i["resource"] for i in propagation[src]["impacted"]]:
            propagation[src]["impacted"].append({"resource": dst, "log": log})

    summary = list(propagation.values())
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[Python] Agent2: results written to {OUTPUT_FILE}.")

if __name__ == "__main__": run()