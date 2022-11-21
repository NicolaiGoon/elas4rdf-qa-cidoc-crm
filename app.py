import flask
from flask import request, jsonify
from answer_extraction import AnswerExtraction
from answer_type_prediction import AnswerTypePrediction
from entity_expansion import expandEntitiesPath, get_entities_from_elas4rdf, get_entities_from_elas4rdf
import entity_expansion
import json
import time

app = flask.Flask(__name__)
# Initialize answer extraction and answer type prediction components
print('Initializing...')
ae = AnswerExtraction()
atp = AnswerTypePrediction()
try:
    with open("./performance.log.json", encoding='utf8') as out:
        log = json.load(out)
except FileNotFoundError:
    log = []
print('\tDONE')

"""
Parameters: question - a natural language question
Returns: question category, answer type, and a list of answers
""" 
@app.route('/answer', methods=['GET'])
def api_answer():

    args = request.args.to_dict()
    if 'question' in args:
        question = args['question']
    else:
        error_output = {'error':True}
        return jsonify(error_output)
   
    entities = get_entities_from_elas4rdf(question,description_label="description")
    print("Entities found: "+str(len(entities)))

    """
    to improve performance when we receive a large number of entities
    we use only the first 10
    """
    if len(entities)>10:
        entities = entities[0:10]

    # ATP
    
    # start = time.time()
    # found_category, found_type = atp.classify_category(question)
    # end = time.time()
    # atp_time = end-start
    # print(found_category,found_type)
    # print("Answer type prediction: ",atp_time)

    # if found_category == "resource":
    #     found_types = atp.classify_resource(question)[0:10]
    # else:
    #     found_types = [found_type]

    found_category = None
    found_type = None
    atp_time = 0

    start = time.time()
    # depth  2 3 4 5
    entities = ae.extend_entities(entities,found_category,found_type,depth=5)
    end = time.time()
    ea_time = end-start
    print("Entity expansion: ",ea_time)
    # return jsonify(entities)
    
    start = time.time()
    answers = ae.answer_extractive(question,entities)
    end = time.time()
    aexctr_time = end-start
    print("Answer extraction: ",aexctr_time)

    response = {
        # "category":found_category,
        # "types":found_types[0],
        "answers":answers
    }

    log.append({
        "ATP" : atp_time,
        "Expansion" : ea_time,
        "AExtraction" : aexctr_time
    })
    out =  open("./performance.log.json","w",encoding="utf8")
    json.dump(log,out)
    return jsonify(response)

@app.route('/', methods=['GET'])
def greet():
    return "Usage: /answer?question=..."
