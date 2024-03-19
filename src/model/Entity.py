import re


class Entity:

    def __init__(self, elas4rdf: dict, description_label: str):
        self.uri = elas4rdf["sub"]
        self.uri_keywords = elas4rdf["sub_keywords"]
        self.ext = elas4rdf["sub_ext"]
        self.text = re.sub(
            r"[\[\]]|@.+", " ", elas4rdf["sub_ext"][description_label]
        ).strip() if description_label in elas4rdf["sub_ext"] else ""
        self.ext_text = None
        self.score = elas4rdf["score"]

    def extend_entity(self, text):
        self.ext_text = self.text + " " + text
