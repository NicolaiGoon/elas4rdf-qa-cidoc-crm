import json
from typing import List, re

import requests

from src.model.Entity import Entity
from src.config import config


class Elas4rdfClient():
    def __init__(self):
        self.base_url = config['ELAS4RDF_URL']

    def __initialize_index(self):
        payload = {
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
        }
        requests.request("POST",
                         self.base_url + "/elas4rdf-rest/datasets",
                         headers={'Content-Type': 'application/json'},
                         json=payload
                         )

    def get_entities(self, query, description_label, size=1000) -> List[Entity]:
        """
        Get entities from the elas4rdf search service
        The parameter 'size' defines the number of triples to use to create the entities
        """
        url = self.base_url + "/elas4rdf-rest/high-level"

        # the id of the elastic search index
        index_id = "cidoc_crm"

        params = {"id": index_id, "query": query, "size": str(size)}

        headers = {"Accept": "application/json"}
        response = requests.get(url, params=params, headers=headers)

        response_json = response.json()

        # init index
        if "triples" not in response_json["results"]:
            self.__initialize_index()

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

            entities = [Entity(t, description_label) for t in filtered_triples]

            return entities
        except Exception as error:
            print(error)
            return []
