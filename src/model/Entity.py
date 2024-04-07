import re


class Entity:

    def __init__(self, elas4rdf_triple: dict, description_label: str):
        self.uri = elas4rdf_triple["sub"]
        self.uri_keywords = elas4rdf_triple["sub_keywords"]
        self.ext = elas4rdf_triple["sub_ext"]
        self.text = re.sub(
            r"[\[\]]|@.+", " ", elas4rdf_triple["sub_ext"][description_label]
        ).strip() if description_label in elas4rdf_triple["sub_ext"] else ""
        self.ext_text = None
        self.score = elas4rdf_triple["score"]

    def __str__(self):
        return str({
            "uri": self.uri,
            "uri_keywords": self.uri_keywords,
            "ext": self.ext,
            "text": self.text,
            "ext_text": self.ext_text,
            "score": self.score,
        })
    def extend_entity(self, text):
        self.ext_text = self.text + " " + text
