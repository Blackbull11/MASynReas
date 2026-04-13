import requests, json, sys

ENDPOINT  = "http://localhost:8890/sparql"
OUTPUT_FILE = "result_major.json"
QUERY = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX noria:   <https://w3id.org/noria/ontology/>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?resource ?logMessage ?repairLabel ?app ?team
WHERE {
  ?tt a noria:TroubleTicket .
  ?tt dcterms:relation ?log .
  ?log noria:alarmPerceivedSeverity
       <https://w3id.org/noria/kos/Notification/Severity/PerceivedSeverity/major> .
  ?log noria:logText ?logMessage .
  ?log noria:logOriginatingManagedObject ?resource .
  ?log noria:alarmProposedRepairAction ?repair .
  ?repair rdfs:label ?repairLabel .
  ?resource noria:resourceForApplication ?app .
  ?resource noria:resourceManagedBy ?team .
}
"""

def local_name(uri): return uri.split("/")[-1]

def run():
    print("[Python] Agent1: querying critical alarms...")
    r = requests.get(ENDPOINT,
                     headers={"Accept": "application/sparql-results+json"},
                     params={"query": QUERY, "format": "application/sparql-results+json"},
                     timeout=30)
    r.raise_for_status()
    bindings = r.json()["results"]["bindings"]
    print(f"[Python] Agent1: {len(bindings)} result(s).")

    # Summarize for coordinator: list of critical alarm objects
    summary = [{
        "resource":    local_name(b["resource"]["value"]),
        "message":     b["logMessage"]["value"],
        "repair":      b["repairLabel"]["value"],
        "app":         local_name(b["app"]["value"]),
        "team":        local_name(b["team"]["value"]),
        "has_repair":  True
    } for b in bindings]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[Python] Agent1: results written to {OUTPUT_FILE}.")

if __name__ == "__main__": run()