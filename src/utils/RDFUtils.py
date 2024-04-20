import os
import re
from typing import List


def cidoc_uri_to_str(uri: str) -> str:
    """
    Convert a cidoc-crm uri to a readable string
    """
    strip_prefix = re.sub(r"^[A-Za-z0-9]*_", "", uri[uri.rindex("/") + 1:])
    return strip_prefix.replace("_", " ")


def triples_to_text(triples: str) -> str:
    separator = ". "
    triples = separator.join(triples)
    return re.sub(r"\s{2,}", " ", triples).replace(" .", ".")


def graph_to_triples(graph: dict, ignore_previous_depth: bool, depth: int = 1) -> List[str] or []:
    """
    Converts the result of a SPARQL query with GraphDB property path to readable triples
    """
    triples = []
    try:
        for row in graph["results"]["bindings"]:
            # print(row)

            # if ignorePreviousDepth is true, skip triple if it does not belong to the current depth
            if ignore_previous_depth and int(row["depth"]["value"]) != depth - 1:
                continue

            # take value if the subject is literal, then try rdfs:label and last try rdf:value
            if row["s"]["type"] == "literal":
                subject = row["s"]["value"]
            elif "sLabel" in row:
                subject = row["sLabel"]["value"]
            elif "sValue" in row:
                subject = row["sValue"]["value"]
            else:
                subject = os.path.basename(row["s"]["value"])

            predicate = cidoc_uri_to_str(row["p"]["value"])

            # same as subject
            if row["o"]["type"] == "literal":
                obj = row["o"]["value"]
            elif "oLabel" in row:
                obj = row["oLabel"]["value"]
            elif "oValue" in row:
                obj = row["oValue"]["value"]
            else:
                obj = os.path.basename(row["o"]["value"])

            # if one property of the triple is empty skip it
            if not subject or not obj or not predicate:
                continue
            triples.append(re.sub(r"\s{2,}", " ", subject + " " + predicate + " " + obj))
        # remove dublicates
        return [t for i, t in enumerate(triples) if triples.index(t) == i]
    except Exception as err:
        print(err)
        return []
