from typing import List

from src.clients.SparqlDBClient import SparqlDBClient


class GraphDBClient(SparqlDBClient):

    def sparql_query(self, query) -> List[dict]:
        pass
