from copy import copy
from distutils.log import warn
import requests
import json
import re
import copy
import time

"""
This module contains methods to retrieve entities
from the elas4rdf search service, retrieve
RDF nodes that match the answer type to a question
and generate sentences to extend entity descriptions
"""

SPARQL_URL = "http://127.0.0.1:8890/sparql"
ELAS4RDF_SEARCH_URL = "http://localhost:8080/elas4rdf-rest-0.0.1-SNAPSHOT"

def sparql_query(query_string):
    # Execute a query on a SPARQL endpoint
    # url = "http://139.91.183.46:8899/sparql"
    # url = "http://dbpedia.org/sparql"
    url = SPARQL_URL
    payload = {
        "query": query_string,
        "default-graph-uri": "http://localhost:8890/cidoc-crm"
    }
    headers = {"Accept":"application/json"}
    response = requests.get(url,params=payload,headers=headers)
    try:
        # normal 
        response_json =  response.json()
        keys = response_json['head']['vars']
        results = []
        for b in response_json['results']['bindings']:
            result = {}
            for k in keys:
                result[k] = b[k]['value']
            results.append(result)
    except:
        # graph cosntruction
        try:
            results = response.json()
        except:    
            print("sparql error")
            results = [] 
    return results



def resource_sentences(entity_uri,type_uri):
    """ Find subjects of the entity that match the answer type
    and generate sentences of the form "entity predicate label answer"
    """
    sentences = []
    query_string_o = ("select distinct str(?pl) as ?pLabel ?a where {{"
                        "<{0}> ?p ?a . "
                        "?p rdfs:label ?pl . "
                        "<{1}> owl:equivalentClass ?eq . "
                        "?a rdf:type ?eq . "
                        "FILTER(lang(?pl) = 'en' || lang(?pl) = '') "
                    "}}").format(entity_uri,type_uri)
    response = sparql_query(query_string_o)
    if len(response)>20:
    	response = response[0:20]
    for r in response:
        sentences.append(entity_to_str(entity_uri)+' '+r['pLabel']+' '+entity_to_str(r['a']))
    return sentences

def literal_sentences(entity_uri,literal_type):
    """ Find literal subjects of the entity that match
    the answer type and generate sentences of the form
    "entity predicate label answer"
    """
    sentences = []
    entity_string = entity_to_str(entity_uri)
    if literal_type == 'date':
        query_string = ("select str(?answer) as ?a str(?pl) as ?pLabel where {{"
                        "<{}> ?p ?answer . "
                        "?p rdfs:range xsd:date . "
                        "?p rdfs:label ?pl . "
                        "FILTER(isLiteral(?answer)) "
                        "FILTER(lang(?pl) = 'en' || lang(?pl) = '') "
                        "}}").format(entity_uri)  
        response = sparql_query(query_string)      
        for r in response:
            sentences.append(entity_string+' '+r['pLabel']+' '+r['a'])
    else: # if number or string
        query_string = ("select str(?answer) as ?a str(?pl) as ?pLabel where {{"
                        "<{}> ?p ?answer . "
                        "?p rdfs:range ?answerType . "
                        "?p rdfs:label ?pl . "
                        "FILTER(isLiteral(?answer)) "
                        "FILTER(lang(?pl) = 'en' || lang(?pl) = '') "
                        "}}").format(entity_uri)         
        response = sparql_query(query_string)
        if len(response)>20:
    	    response = response[0:20]
        for r in response:
            if len(r['a'])<100:
                isNumber = r['a'].replace('.','',1).isdigit()
                if(literal_type == 'number' and isNumber):
                    sentences.append(entity_string+' '+r['pLabel']+' '+r['a'])
                elif(literal_type =='string' and (not isNumber)):
                    sentences.append(entity_string+' '+r['pLabel']+' '+r['a'])

    return sentences

def entity_to_str(e):
    # Convert a dbpedia uri to a readable string
    return e[e.rindex("/")+1:].replace('_',' ')

def get_entities_from_elas4rdf(query, size=1000):
    """
    Get entities from the elas4rdf search service
    The parameter 'size' defines the number of triples to use to create the entities
    """
    url = ELAS4RDF_SEARCH_URL + "/high-level"
    # the id of the elastic search index
    index_id = "cidoc_crm"
    
    payload = {
        "id":index_id,
        "query": query,
        "size": str(size)
    }
    
    headers = {"Accept":"application/json"}
    response = requests.get(url,params=payload,headers=headers)
    
    response_json = response.json()

    try:
        triples = response_json["results"]["triples"]
        filtered_triples = list(filter(lambda t: t["sub_ext"] ,triples)) 
        
        entities =  [{
            "uri" : t["sub"],
            "uri_keywords" : t["sub_keywords"],
            "ext" : t["sub_ext"],
            "text" : re.sub(r"[\[\]]","",t["sub_ext"]["description"]).strip() if "description" in t["sub_ext"] else "",
            "score":t["score"]
        } for t in filtered_triples]
        
        # filter dublicate subjects in triples   
        return list({e["uri"]:e for e in entities}.values())
    except Exception as error : 
        print(error)
        return []

def expandEntitiesPath(entities,depth=1):   
    '''
    Expands entity description with triples derived from the entity path 
    '''
    
    if(depth == 1):
        query = ("construct {{"
        "?s ?p ?o ."
        "}}"
        "where {{"
        "bind(<{0}> as ?s) ."
        "?s ?p ?o ."
        "}}")
    elif(depth == 2):
        query = ("construct {{"
        "?s ?p ?o ."
        "?o ?p2 ?o2 ."
        "}}"
        "where {{"
        "bind(<{0}> as ?s) ."
        "?s ?p ?o ."
        "optional {{"
        "?o ?p2 ?o2 ."
        "}}"
        "}}")
    elif(depth == 3):
        query = ("construct {{"
        "?s ?p ?o ."
        "?o ?p2 ?o2 ."
        "?o2 ?p3 ?o3 ."
        "}}"
        "where {{"
        "bind(<{0}> as ?s) ."
        "?s ?p ?o ."
        "optional {{"
        "?o ?p2 ?o2 ."
        "optional {{"
            "?o2 ?p3 ?o3 ."
            "}}"
        "}}"
        "}}")
    else:
        raise Exception("depth must be in the range of 1-3")

    extended = []
    start = time.time()
    for e in entities:
        subgTime = time.time()
        subgraph = sparql_query(query.format(e["uri"]))
        subgTime = time.time() - subgTime
        print("Subgraph construction  for {0} took: {1}".format(e['uri'],subgTime))
        text = cidocGraphToText(subgraph)
        ext = copy.deepcopy(e)
        ext['text'] += ' ' + text
        extended.append(ext)
    end = time.time()
    print("Entity Path expand took: {0}".format(end-start))
    return extended

def cidoc_uri_to_str(e):
    '''
    Convert a cidoc-crm uri to a readable string
    '''
    strip_prefix = re.sub(r'^[A-Za-z0-9]*_','',e[e.rindex("/")+1:])
    return strip_prefix.replace('_',' ')

def cidocGraphToText(g,labelName="prefLabel"):
    '''
    Converts a cidoc-crm subgraph to text by connecting the triples and replacing ids with labels
    '''

    # label id map
    labelDict = dict()
    text = ""
    for s in g:
        for p in g[s]:
            # add triple
            if("cidoc-crm" in p):
                objects = ""
                for o in g[s][p]: 
                    if(o["type"] == "uri"):
                        objects += o["value"] + ", "
                # replace last comma and replace the previous one with an "and"
                objects =  ' and '.join(objects[:-2].rsplit(",",1))
                text += " "+s+" "+cidoc_uri_to_str(p)+" "+objects+"."
            # add label to the dictionary
            elif(labelName in p):
                labelDict[s]  = g[s][p][0]["value"]
    # replace id with label
    for key in labelDict:
        text = text.replace(key,labelDict[key])
    return re.sub(r'\s{2,}',' ',text).replace(" .",".")