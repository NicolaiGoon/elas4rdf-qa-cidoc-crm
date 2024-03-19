from typing import List

from src.model.Entity import Entity
from src.config import config


class Elas4rdfClient():
    def __init__(self):
        self.base_url = config['ELAS4RDF_URL']

    def get_entities(self) -> List[Entity]:
        pass
