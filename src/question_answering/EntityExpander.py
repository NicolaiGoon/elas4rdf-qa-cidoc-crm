from typing import List

from src.clients.SparqlDBClient import SparqlDBClient
from src.model.Entity import Entity


class EntityExpander:
    def __init__(self, sparql_client: SparqlDBClient):
        self.sparql_client = sparql_client

    def extend_entities(self, entities: List[Entity], depth: int = 1, ignore_previous_depth=False) -> List[Entity]:
        pass
