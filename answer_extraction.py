from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import torch
import entity_expansion as expansion
from boolean_question import BoolQ


class AnswerExtraction:
    # This class contains methods for the answer extraction stage

    def __init__(self):
        # Initalisation of pretrained extractive QA model
        model_name = "deepset/roberta-base-squad2"
        # tokenizer = RobertaTokenizer.from_pretrained(model_name)
        # model = RobertaForQuestionAnswering.from_pretrained(model_name)
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print("Using Device: " + str(device))
        self.pipeline = pipeline('question-answering',
                                 model=model_name, tokenizer=model_name)
        self.boolean_pipeline = BoolQ()

    def answer_extractive(self, question, entities, q_type="factoid"):
        print("starting answer extraction")
        # Obtain a question from each given entity
        answers = []
        for e in entities:
            # print('ans '+e['uri'])
            # print(e)
            # emtpy text
            if e["text"] == "" or e["text"] == " ":
                answers.append(
                    {"entity": e["uri"], "answer": "", "score": 0, "text": ""}
                )
            else:
                output = self.pipeline(
                    {"question": question, "context": e["text"]}) if q_type == "factoid" else self.boolean_pipeline.predict(e["text"], question)
                # cant find answer
                if output == []:
                    answers.append(
                        {"entity": e["uri"], "answer": "",
                            "score": 0, "text": ""}
                    )
                else:
                    # highlighted_text = e['text'][0:output['start']]+'<b>'+e['text'][output['start']:output['end']]+'</b>'+e['text'][output['end']:]
                    final_answer = ("Yes" if output else "No") if isinstance(
                        output, bool) else output["answer"]
                    score = (self.boolean_pipeline.prediction_details()[
                             str(output).lower()+' confidence']) if isinstance(output, bool) else round(output["score"], 3)
                    answers.append(
                        {
                            "entity": e["uri"],
                            "answer":  final_answer,
                            "score": score,
                            "text": e["text"],
                        }
                    )
        return sorted(answers, key=lambda k: k["score"], reverse=True)

    def extend_entities(
        self, entities, category, atype, depth=1, ignorePreviousDepth=False
    ):
        # Extend entity descriptions with RDF nodes matching the answer type if it is not resource,
        # and if it is resource create text from a subgraph starting from the resource
        extended = []

        # Entity Path Expansion
        if category == "resource" or (category == None and atype == None):
            # type_uri = 'http://dbpedia.org/ontology/'+atype
            # sentences = expansion.resource_sentences(e['uri'],type_uri)
            return expansion.expandEntitiesPath(
                entities, depth, ignorePreviousDepth=ignorePreviousDepth
            )
        else:
            for e in entities:
                # print('ext '+e['uri'])
                sentences = set(expansion.literal_sentences(e["uri"], atype))
                new_text = (e["text"] + " " + ". ".join(sentences)).strip()
                # print(new_text)
                extended.append({"uri": e["uri"], "text": new_text})
        return extended
