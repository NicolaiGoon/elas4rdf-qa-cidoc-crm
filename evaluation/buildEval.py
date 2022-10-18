import json
import requests

SPARQL_URL = "http://127.0.0.1:8890/sparql"

def sparql_query(query_string):
    url = SPARQL_URL
    payload = {
        "query": query_string,
        "default-graph-uri": "http://localhost:8890/cidoc-crm"
    }
    headers = {"Accept":"application/json"}
    response = requests.get(url,params=payload,headers=headers)
    return response.json()

query = '''
select distinct ?sL ?whoL ?placeL ?timeL {
?s rdf:type crm:E5_Event .
?s skos:prefLabel ?sL .
FILTER (lang(?sL) = 'en') .
optional {?s crm:P14_carried_out_by ?who .
?who skos:prefLabel ?whoL}
optional {?s crm:P7_took_place_at ?place .
?place skos:prefLabel ?placeL}
optional {?s crm:P4_has_time-span ?time .
?time skos:prefLabel ?timeL}
}
'''

dataset = []
res = sparql_query(query)
id = 0
for obj in res["results"]["bindings"]:
    for key in obj:
        if key == "timeL":
            dataset.append({
                "id":id,
                "question" : "When did the " + obj["sL"]["value"] + " take place?",
                "answers" : [obj["timeL"]["value"]]
            })
        if key == "placeL":
            id += 1
            dataset.append({
                "id":id,
                "question" : "Where the " + obj["sL"]["value"] + " took place?",
                "answers" : [obj["placeL"]["value"]]
            })
        elif key == "whoL":
            id += 1
            dataset.append({
                "id":id,
                "question" : "Who accomplished the " + obj["sL"]["value"],
                "answers" : [obj["whoL"]["value"]]
            })

with open("./evaluation/evalcoll.json","w",encoding="utf-8") as outfile:
    json.dump(dataset,outfile)
