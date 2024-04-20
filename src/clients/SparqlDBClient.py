from typing import List

from src.config import config


class SparqlDBClient:
    def __init__(self):
        self.base_url = config['SPARQL_URL']

    def sparql_query(self, query) -> dict:
        pass
