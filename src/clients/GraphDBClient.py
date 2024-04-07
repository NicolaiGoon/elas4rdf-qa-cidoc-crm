from typing import List

import requests

from src.clients.SparqlDBClient import SparqlDBClient
from src.config import config


class GraphDBClient(SparqlDBClient):

    def sparql_query(self, query) -> List[dict]:
        params = {
            "query": query
        }
        headers = {"Accept": "application/json"}
        repo = config["GRAPH_DB_REPO"]
        url = self.base_url + f"/repositories/{repo}"
        response = requests.request("GET", url, params=params, headers=headers)

        return response.json()
