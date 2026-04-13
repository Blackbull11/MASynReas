import requests, json, sys

ENDPOINT   = "http://localhost:8890/sparql"
OUTPUT_FILE = "result_unhandled.json"

QUERY = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX noria:   <https://w3id.org/noria/ontology/>

SELECT ?resource ?logMessage ?app ?team ?loggingTime
WHERE {
  ?tt a noria:TroubleTicket .
  ?tt dcterms:relation ?log .
  ?log noria:alarmPerceivedSeverity
       <https://w3id.org/noria/kos/Notification/Severity/PerceivedSeverity/major> .
  ?log noria:logText ?logMessage .
  ?log noria:logOriginatingManagedObject ?resource .
  ?log noria:loggingTime ?loggingTime .
  ?resource noria:resourceForApplication ?app .
  ?resource noria:resourceManagedBy ?team .
  FILTER NOT EXISTS { ?log noria:alarmProposedRepairAction ?repair . }
}
"""

def local_name(uri): return uri.split("/")[-1]

def run():
    print("[Python] Agent3: querying unhandled alarms...")
    r = requests.get(ENDPOINT,
                     headers={"Accept": "application/sparql-results+json"},
                     params={"query": QUERY, "format": "application/sparql-results+json"},
                     timeout=30)
    r.raise_for_status()
    bindings = r.json()["results"]["bindings"]
    print(f"[Python] Agent3: {len(bindings)} unhandled alarm(s).")

    summary = [{
        "resource":    local_name(b["resource"]["value"]),
        "message":     b["logMessage"]["value"],
        "app":         local_name(b["app"]["value"]),
        "team":        local_name(b["team"]["value"]),
        "time":        b["loggingTime"]["value"],
        "has_repair":  False
    } for b in bindings]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[Python] Agent3: results written to {OUTPUT_FILE}.")

if __name__ == "__main__": run()