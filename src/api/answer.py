from fastapi import APIRouter

from src.clients.Elas4rdfClient import Elas4rdfClient
from src.clients.GraphDBClient import GraphDBClient
from src.question_answering.EntityExpander import EntityExpander
from src.question_answering.ModelLoader import ModelLoader
from src.question_answering.TrasnformerAnswerExtraction import TransformerAnswerExtraction
from src.model.QAResponse import QAResponse

router = APIRouter()

model_loader = ModelLoader(model_name="deepset/roberta-base-squad2")
answer_extraction = TransformerAnswerExtraction(model_loader=model_loader)
elas4rdf_client = Elas4rdfClient()
graphdb_client = GraphDBClient()
entity_expansion = EntityExpander(graphdb_client)


@router.get("/")
async def get_answer(
        question: str,
        entity: str = None,
        depth: int = 1,
        threshold: float = 1.0,
        ignore_previous_depth: bool = False):
    entities = elas4rdf_client.get_entities()
    print(entities)
    entities = entity_expansion.extend_entities(entities, depth=depth, ignore_previous_depth=ignore_previous_depth)
    context = "milo has created everything"
    a = answer_extraction.extract_answer(question=question, passage=context)
    print(a)
    response = QAResponse(entity=entity, answer=a["answer"], score=a["score"], text=context)
    return response
