from copy import copy
from distutils.log import warn
import os
import requests
import json
import re
import copy
import time
from itertools import groupby

"""
This module contains methods to retrieve entities
from the elas4rdf search service, retrieve
RDF nodes that match the answer type to a question
and generate sentences to extend entity descriptions
"""

SPARQL_URL = "http://192.168.1.5:7200/repositories/cidoc-crm"
ELAS4RDF_SEARCH_URL = "http://127.0.0.1:8080/elas4rdf-rest"

def sparql_query(query_string, headers="application/json"):
    # Execute a query on a SPARQL endpoint

    payload = {
        "query": query_string,
        # "default-graph-uri": "http://localhost:8890/cidoc-crm"
    }
    headers = {"Accept": headers}
    response = requests.get(SPARQL_URL, params=payload, headers=headers)
    # print(response.text)
    try:
        results = response.json()
    except:
        print("sparql error")
        print(response)
        results = []
    return results


def resource_sentences(entity_uri, type_uri):
    """Find subjects of the entity that match the answer type
    and generate sentences of the form "entity predicate label answer"
    """
    sentences = []
    query_string_o = (
        "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>"
        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
        "select distinct str(?pl) as ?pLabel ?a where {{"
        "<{0}> ?p ?a . "
        "?p rdfs:label ?pl . "
        "<{1}> owl:equivalentClass ?eq . "
        "?a rdf:type ?eq . "
        "FILTER(lang(?pl) = 'en' || lang(?pl) = '') "
        "}}"
    ).format(entity_uri, type_uri)
    response = sparql_query(query_string_o)

    if len(response) > 20:
        response = response[0:20]
    for r in response:
        sentences.append(
            entity_to_str(entity_uri) + " " + r["pLabel"] + " " + entity_to_str(r["a"])
        )
    return sentences


def literal_sentences(entity_uri, literal_type):
    """Find literal subjects of the entity that match
    the answer type and generate sentences of the form
    "entity predicate label answer"
    """
    sentences = []
    # entity_string = entity_to_str(entity_uri)
    if literal_type == "date":
        query_string = (
            "PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>"
            "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>"
            "prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
            "select ?sL (str(?answer) as ?a) (str(?pl) as ?pLabel) where {{"
            "{{"
            "	<{0}> ?p ?answer ; skos:prefLabel ?sL ."
            "?p rdfs:range xsd:date . "
            "?p rdfs:label ?pl ."
            "FILTER(isLiteral(?answer)) "
            "FILTER(lang(?pl) = 'en' || lang(?pl) = '') "
            "}}"
            "UNION {{"
            "<{0}> crm:P4_has_time-span ?ts ; skos:prefLabel ?sL ."
            "FILTER(lang(?sL) = 'en' || lang(?sL) = '') ."
            "?ts ?pl ?answer ."
            "FILTER ( datatype(?answer) = xsd:date || datatype(?answer) = xsd:string) ."
            "}}"
            "}}"
        ).format(entity_uri)
        response = sparql_query(query_string)
        if response == []:
            return ""
        for r in response["results"]["bindings"]:
            prop = r["pLabel"]["value"]
            if "cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin" in prop:
                prop = "began on"
            elif "cidoc-crm.org/cidoc-crm/P82b_end_of_the_end" in prop:
                prop = "ended at"
            elif "www.w3.org/2004/02/skos/core#prefLabel" in prop:
                prop = "has time span"
            sentences.append(r["sL"]["value"] + " " + prop + " " + r["a"]["value"])
    else:  # if number or string or boolean
        if literal_type == "string" or literal_type == "number":
            xsdType = "string"
        else:
            xsdType = "boolean"

        query_string = (
            "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>"
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>"
            "select ?sL (str(?answer) as ?a) (str(?pl) as ?pLabel) where {{"
            "<{0}> ?p ?answer . "
            "?p rdfs:range ?answerType . "
            "<{0}> skos:prefLabel ?sL . "
            "?p rdfs:label ?pl . "
            "FILTER(isLiteral(?answer)) "
            "FILTER ( datatype(?answer) = xsd:{1}) ."
            "FILTER(lang(?pl) = 'en' || lang(?pl) = '') "
            "}}"
        ).format(entity_uri, xsdType)
        response = sparql_query(query_string)
        if response == []:
            return ""
        if len(response["results"]["bindings"]) > 20:
            response["results"]["bindings"] = response["results"]["bindings"][0:20]
        for r in response["results"]["bindings"]:
            if len(r["a"]["value"]) < 100:
                isNumber = r["a"]["value"].replace(".", "", 1).isdigit()
                if literal_type == "number" and isNumber:
                    sentences.append(
                        r["sL"]["value"]
                        + " "
                        + r["pLabel"]["value"]
                        + " "
                        + r["a"]["value"]
                    )
                else:
                    sentences.append(
                        r["sL"]["value"]
                        + " "
                        + r["pLabel"]["value"]
                        + " "
                        + r["a"]["value"]
                    )

    return sentences


def entity_to_str(e):
    # Convert a dbpedia uri to a readable string
    return e[e.rindex("/") + 1 :].replace("_", " ")


def get_entities_from_elas4rdf(query, description_label, size=1000):
    """
    Get entities from the elas4rdf search service
    The parameter 'size' defines the number of triples to use to create the entities
    """
    url = ELAS4RDF_SEARCH_URL + "/high-level"
    # the id of the elastic search index
    index_id = "cidoc_crm"

    payload = {"id": index_id, "query": query, "size": str(size)}

    headers = {"Accept": "application/json"}
    response = requests.get(url, params=payload, headers=headers)

    response_json = response.json()

    # init index
    if "triples" not in response_json["results"]:
        init_payload = json.dumps({
            "id": "cidoc_crm",
            "index.name": "cidoc_ext_index",
            "index.fields": {
                "subjectKeywords": 1,
                "predicateKeywords": 1,
                "objectKeywords": 2,
                "rdfs_type_sub": 1,
                "rdfs_comment_sub": 1,
                "rdfs_label_sub": 1
            }
            })
        response_init = requests.request("POST",
            ELAS4RDF_SEARCH_URL+"/datasets",
            headers={'Content-Type': 'application/json'},
            data=init_payload)
        assert response_init.status_code == 200
        response = requests.get(url, params=payload, headers=headers)
        response_json = response.json()


    try:
        triples = response_json["results"]["triples"]
        # filter triples , unique subject sorted by score
        filtered_triples = {}
        for obj in triples:
            sub = obj["sub"]
            if sub in filtered_triples:
                if obj["score"] > filtered_triples[sub]["score"]:
                    filtered_triples[sub] = obj
            else:
                filtered_triples[sub] = obj
        filtered_triples = list(filtered_triples.values())

        entities = [
            {
                "uri": t["sub"],
                "uri_keywords": t["sub_keywords"],
                "ext": t["sub_ext"],
                "text": re.sub(
                    r"[\[\]]|@.+", " ", t["sub_ext"][description_label]
                ).strip()
                if description_label in t["sub_ext"]
                else "",
                "score": t["score"],
            }
            for t in filtered_triples
        ]

        return entities
    except Exception as error:
        print(error)
        return []


def expandEntitiesPath(
    entities, depth=1, isGraphDB=True, ignorePreviousDepth=False, filterIdentifier=False
):
    """
    Expands entity description with triples derived from the entity path
    """

    if isGraphDB:
        query = (
            "PREFIX path: <http://www.ontotext.com/path#>"
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
            "PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>"
            "SELECT DISTINCT (?start as ?s) (?property as ?p) (?end as ?o) (?startLabel as ?sLabel) "
            "(?endLabel as ?oLabel) (?startValue as ?sValue) (?endValue as ?oValue) (?index as ?depth) WHERE {{"
            "{{"
            " SELECT ?start ?property ?end ?index "
            "WHERE {{"
            "VALUES (?src) {{"
            "(<{0}>)"
            "}}"
            "SERVICE path:search {{"
            "<urn:path> path:findPath path:allPaths ;"
            "path:sourceNode ?src ;"
            "path:destinationNode ?dst ;"
            "path:minPathLength 1 ;"
            "path:maxPathLength {1} ;"
            "path:startNode ?start;"
            "path:propertyBinding ?property ;"
            "path:endNode ?end;"
            "path:resultBindingIndex ?index ;"
            "path:pathIndex ?path ."
            "}}"
            "}}"
            "}}"
            " OPTIONAL {{"
            "   ?start rdfs:label ?startLabel ."
            '   FILTER(lang(?startLabel) = "en" || lang(?startLabel) = "")'
            "}}"
            "OPTIONAL {{"
            "?start rdf:value ?startValue"
            "}}"
            " OPTIONAL {{"
            "     ?end rdfs:label ?endLabel ."
            '     FILTER(lang(?endLabel) = "en" || lang(?endLabel) = "")'
            "}}"
            "OPTIONAL {{"
            "?end rdf:value ?endValue"
            "}}"
            ' FILTER(REGEX(STR(?property), "http://www.cidoc-crm.org/cidoc-crm")) .'
            "}} ORDERBY DESC(?index)"
        )
    else:
        query = (
            "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>"
            "PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>"
            "CONSTRUCT {{ ?s ?p ?o}}"
            "WHERE {{"
            "{{"
            "<{0}> (crm:|!crm:){{,{1}}} ?s ."
            "?s ?p ?o ."
            'FILTER(REGEX(STR(?p), "^http://www.cidoc-crm.org/cidoc-crm")) .'
            "}}"
            "UNION {{"
            "<{0}> (crm:|!crm:){{,{2}}} ?s ."
            "?s ?p ?o ."
            'FILTER(REGEX(STR(?p), "^http://www.w3.org/2004/02/skos/core#prefLabel")) .'
            "}}"
            "}}"
        )

    extended = []
    start = time.time()
    for e in entities:
        subgTime = time.time()
        if isGraphDB:
            q_formatted = query.format(e["uri"], depth)
            headers = "application/json"
        else:
            q_formatted = query.format(e["uri"], depth - 1, depth)
            headers = "application/ld+json"
        subgraph = sparql_query(q_formatted, headers=headers)
        # print(q_formatted)
        subgTime = time.time() - subgTime
        # print("Subgraph construction  for {0} took: {1}".format(e['uri'],subgTime))
        # text = cidocGraphToText(subgraph)

        # works with GraphDB
        text = cidocGraphToTextV2(
            subgraph, ignorePreviousDepth=ignorePreviousDepth, depth=depth
        )

        ext = copy.deepcopy(e)
        ext["text"] += " " + text
        extended.append(ext)
    end = time.time()
    # print("Entity Path expand took: {0}".format(end-start))
    return extended


def cidoc_uri_to_str(e):
    """
    Convert a cidoc-crm uri to a readable string
    """
    strip_prefix = re.sub(r"^[A-Za-z0-9]*_", "", e[e.rindex("/") + 1 :])
    return strip_prefix.replace("_", " ")


# def cidocGraphToText(g,labelName="prefLabel"):
#     '''
#     Converts a cidoc-crm subgraph to text by connecting the triples and replacing ids with labels
#     '''

#     # label id map
#     labelDict = dict()
#     text = ""
#     for s in g:
#         for p in g[s]:
#             # add triple
#             if("cidoc-crm" in p):
#                 objects = ""
#                 for o in g[s][p]:
#                     if(o["type"] == "uri"):
#                         objects += o["value"] + ", "
#                 # replace last comma and replace the previous one with an "and"
#                 objects =  ' and '.join(objects[:-2].rsplit(",",1))
#                 text += " "+s+" "+cidoc_uri_to_str(p)+" "+objects+"."
#             # add label to the dictionary
#             elif(labelName in p):
#                 labelDict[s]  = g[s][p][0]["value"]
#     # replace id with label
#     for key in labelDict:
#         text = text.replace(key,labelDict[key])
#     return re.sub(r'\s{2,}',' ',text).replace(" .",".")


def cidocGraphToText(g, labelName="prefLabel"):
    """
    Converts a cidoc-crm subgraph to text by connecting the triples and replacing ids with labels
    json-ld
    """
    # map uri to label
    labelDict = dict()
    # final text
    text = ""
    print(g)
    if "@graph" not in g:
        return text
    for node in g["@graph"]:
        uri = node["@id"]
        label = node[labelName]
        if isinstance(label, list):
            label = label[0]
        if isinstance(label, dict):
            label = label["@value"]
        labelDict[uri] = label
        for predicate in node.keys():
            if predicate != "@id" and predicate != labelName:
                objUri = node[predicate]
                if isinstance(objUri, list):
                    objUriText = ""
                    for x in objUri:
                        if isinstance(x, dict):
                            objUriText += x["@value"] + ", "
                        else:
                            objUriText += x + ", "
                    # replace last comma and replace the previous one with an "and"
                    objUriText = " and ".join(objUriText[:-2].rsplit(",", 1))
                    text += (
                        " "
                        + uri
                        + " "
                        + cidoc_uri_to_str(
                            "http://www.cidoc-crm.org/cidoc-crm/" + predicate
                        )
                        + " "
                        + objUriText
                        + "."
                    )
                else:
                    text += (
                        " "
                        + uri
                        + " "
                        + cidoc_uri_to_str(
                            "http://www.cidoc-crm.org/cidoc-crm/" + predicate
                        )
                        + " "
                        + objUri
                        + "."
                    )
    # replace id with label
    # print(labelDict)
    for key in labelDict:
        text = text.replace(key, labelDict[key])
    return re.sub(r"\s{2,}", " ", text).replace(" .", ".")


def cidocGraphToTextV2(g, ignorePreviousDepth=False, depth=0):
    """
    Converts the result of a SPARQL query with GraphDB property path to readable triples
    """
    # print(g)
    text = []
    try:
        for row in g["results"]["bindings"]:
            # print(row)

            # if ignorePreviousDepth is true, skip triple if it does not belong to the current depth
            if ignorePreviousDepth and int(row["depth"]["value"]) != depth - 1:
                continue

            # take value if the subject is literal, then try rdfs:label and last try rdf:value
            if row["s"]["type"] == "literal":
                subject = row["s"]["value"]
            elif "sLabel" in row:
                subject = row["sLabel"]["value"]
            elif "sValue" in row:
                subject = row["sValue"]["value"]
            else:
                subject = os.path.basename(row["s"]["value"])

            predicate = cidoc_uri_to_str(row["p"]["value"])

            # same as subject
            if row["o"]["type"] == "literal":
                obj = row["o"]["value"]
            elif "oLabel" in row:
                obj = row["oLabel"]["value"]
            elif "oValue" in row:
                obj = row["oValue"]["value"]
            else:
                obj = os.path.basename(row["o"]["value"])

            # if one property of the triple is empty skip it
            if not subject or not obj or not predicate:
                continue
            text.append(subject + " " + predicate + " " + obj)
        # text = list(set(text))
        separator = ". "
        text = separator.join(text)
        return re.sub(r"\s{2,}", " ", text).replace(" .", ".")
    except Exception as err:
        print(err)
        return ""
