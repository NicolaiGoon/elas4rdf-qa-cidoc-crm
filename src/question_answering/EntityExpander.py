from typing import List

from src.clients.SparqlDBClient import SparqlDBClient
from src.model.Entity import Entity
from src.utils.RDFUtils import graph_to_triples, triples_to_text


class EntityExpander:
    def __init__(self, sparql_client: SparqlDBClient):
        self.sparql_client = sparql_client

    def literal_to_sentences(self, uri, type):
        pass

    def extend_entities(self, entities: List[Entity], depth: int = 1, ignore_previous_depth=False) -> List[Entity]:

        for e in entities:
            query = f"""
                PREFIX path: <http://www.ontotext.com/path#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
                SELECT DISTINCT (?start as ?s) (?property as ?p) (?end as ?o) (?startLabel as ?sLabel) 
                (?endLabel as ?oLabel) (?startValue as ?sValue) (?endValue as ?oValue) (?index as ?depth) WHERE 
                {{
                    {{
                     SELECT ?start ?property ?end ?index 
                        WHERE {{
                        VALUES (?src) {{
                            (<{e.uri}>)
                        }}
                        SERVICE path:search {{
                            <urn:path> path:findPath path:allPaths ;
                            path:sourceNode ?src ;
                            path:destinationNode ?dst ;
                            path:minPathLength 1 ;
                            path:maxPathLength {depth} ;
                            path:startNode ?start;
                            path:propertyBinding ?property ;
                            path:endNode ?end;
                            path:resultBindingIndex ?index ;
                            path:pathIndex ?path .
                            }}
                        }}
                    }}
                    OPTIONAL {{
                        ?start rdfs:label ?startLabel .
                        FILTER(lang(?startLabel) = "en" || lang(?startLabel) = "")
                    }}
                    OPTIONAL {{
                        ?start rdf:value ?startValue
                    }}
                     OPTIONAL {{
                         ?end rdfs:label ?endLabel .
                         FILTER(lang(?endLabel) = "en" || lang(?endLabel) = "")
                    }}
                    OPTIONAL {{
                        ?end rdf:value ?endValue
                    }}
                    FILTER(REGEX(STR(?property), "http://www.cidoc-crm.org/cidoc-crm")) .
                }} ORDERBY DESC(?index)
            """
            subgraph = self.sparql_client.sparql_query(query)
            triples = graph_to_triples(graph=subgraph, ignore_previous_depth=ignore_previous_depth, depth=depth)
            text = triples_to_text(triples)
            e.extend_entity(text)

        return entities
