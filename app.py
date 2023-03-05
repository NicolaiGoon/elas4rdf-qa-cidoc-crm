import json
import time

import flask
from flask import jsonify, request

from answer_extraction import AnswerExtraction
from entity_expansion import get_entities_from_elas4rdf

app = flask.Flask(__name__)
# Initialize answer extraction component
print("Initializing...")
ae = AnswerExtraction()
print("CIDOC-QA is Up!")

"""
Parameters: question - a natural language question
Returns: question category, answer type, and a list of answers
"""
@app.route("/answer", methods=["GET"])
def api_answer():

    args = request.args.to_dict()
    if "question" in args:
        question = args["question"]
        print("Question: " + question)
    else:
        error_output = {"error": True}
        return jsonify(error_output)

    # use the entity provided
    if "entity" in args:
        entities = [{"uri": args["entity"], "text": ""}]
        print("Provided Entity: " + args["entity"])
        esearch_time = 0
    # use entity search
    else:
        start = time.time()
        entities = get_entities_from_elas4rdf(
            question, description_label="rdfs_comment"
        )
        end = time.time()
        esearch_time = end - start
    print("Entities found: " + str(len(entities)))

    """
    to improve performance when we receive a large number of entities
    we use only the first
    """
    # if len(entities)>10:
    entities = entities[:1]

    if len(entities) == 0:
        return jsonify(
            {"answers": [{"answer": "No entities found for this query", "error": True}]}
        )

    found_category = None
    found_type = None

    # ------------------- #
    try:
        depths = parse_depth(args)
        threshold = parse_threshold(args)
        ignorePreviousDepth = parse_ignore(args)
        if(threshold):
            use_threshold = True
        else:
            use_threshold = False

    except :
        return jsonify({"error":"error in parameters"})
        
    # change the depth array in order to expand each depth for each entity
    # depth 1 2 3 4
    answers = []
    ea_time = 0
    aexctr_time = 0

    for d in depths:

        # Expand Entity Path
        assert len(entities) == 1
        start = time.time()
        ext_entity = ae.extend_entities(
            entities,
            found_category,
            found_type,
            depth=d,
            ignorePreviousDepth=ignorePreviousDepth,
        )

        end = time.time()
        ea_time += end - start

        # Answer Extraction
        assert len(ext_entity) == 1
        start = time.time()
        answer = ae.answer_extractive(question, ext_entity)[0]
        end = time.time()
        aexctr_time += end - start

        answers.append(answer)

        if use_threshold and answer["score"] >= threshold:
            # stop the loop , send the answer
            print(
                "Using Threshold: "
                + str(threshold)
                + ", Answer has score: "
                + str(answer["score"])
            )
            answers = [answer]
            break

    # return jsonify(entities)

    # keep the first highest score
    answers.sort(key=lambda x: x["score"], reverse=True)
    answers = answers[:1]

    total_times = {
        "EntitySearch": esearch_time,
        "PathExpansion": ea_time,
        "AnswerExtraction": aexctr_time,
        "Total": esearch_time + ea_time + aexctr_time,
    }
    print("Total Times: ", total_times)

    response = {
        "answers": answers,
        "time": total_times,
    }

    return jsonify(response)


@app.route("/", methods=["GET"])
def greet():
    return "Usage: /answer?question=..."


def parse_depth(args):
    if "depth" in args and args["depth"].isnumeric() :
        return [int(args["depth"])]
    else:
        return [1, 2, 3, 4]

def parse_threshold(args):
    if "threshold" in args:
        try:
            threshold = float(args["threshold"]) 
            return threshold
        except:
            return False
    return False 

def parse_ignore(args):
    if "ignore_previous_depth" in args:
        return True if args["ignore_previous_depth"].lower() in ["1","true"] else False
    else: return False 


