from enum import Enum, IntEnum

from fastapi import APIRouter

from src.clients.Elas4rdfClient import Elas4rdfClient
from src.clients.GraphDBClient import GraphDBClient
from src.question_answering.EntityExpander import EntityExpander
from src.question_answering.ModelLoader import ModelLoader
from src.question_answering.TrasnformerAnswerExtraction import TransformerAnswerExtraction
from src.question_answering.llama2AnswerExtraction import Llama2
from src.model.QAResponse import QAResponse


class depth_enum(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    ALL = 5


class model_enum(Enum):
    ROBERTA = "roberta"
    # LLAMA2 = "llama2"


class question_type_enum(Enum):
    FACTOID = "factoid"
    BOOL = "boolean"


router = APIRouter()

model_loader = ModelLoader(model_name="deepset/roberta-base-squad2")

answer_extraction = {
    model_enum.ROBERTA.value: TransformerAnswerExtraction(model_loader=model_loader),
    # model_enum.LLAMA2.value: Llama2()

}
elas4rdf_client = Elas4rdfClient()
graphdb_client = GraphDBClient()
entity_expansion = EntityExpander(graphdb_client)


@router.get("/")
async def get_answer(
        question: str,
        entity: str = None,
        depth: depth_enum = depth_enum.ONE.value,
        threshold: float = 1.0,
        ignore_previous_depth: bool = False,
        model: model_enum = model_enum.ROBERTA,
        question_type: question_type_enum = question_type_enum.BOOL
):
    entities = elas4rdf_client.get_entities(
        query=question,
        description_label="rdfs_comment")[:1]

    if depth == depth_enum.ALL.value:
        depths = [1, 2, 3, 4]
    else:
        depths = [depth.value]

    answers = []
    for d in depths:
        extended_entities = entity_expansion.extend_entities(
            entities,
            depth=d,
            ignore_previous_depth=ignore_previous_depth
        )
        entity = extended_entities[0]
        answer = answer_extraction[model.value].extract_answer(
            question=question,
            passage=entity.ext_text
        )
        answer["text"] = entity.ext_text
        answers.append(answer)
        if threshold and answer["score"] >= threshold:
            answers = [answer]
            break
    answers.sort(key=lambda x: x["score"], reverse=True)
    answer = answers[0]
    return QAResponse(
        entity=entity.uri,
        answer=answer["answer"],
        score=answer["score"],
        text=answer["text"]
    )
