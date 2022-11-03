import flask
from flask import request, jsonify
from answer_extraction import AnswerExtraction
from answer_type_prediction import AnswerTypePrediction
from entity_expansion import expandEntitiesPath, get_entities_from_elas4rdf, get_entities_from_elas4rdf
import entity_expansion
import json

app = flask.Flask(__name__)
# Initialize answer extraction and answer type prediction components
print('Initializing...')
ae = AnswerExtraction()
atp = AnswerTypePrediction()
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
   
    entities = get_entities_from_elas4rdf(question)


    """
    to improve performance when we receive a large number of entities
    we use only the first 10
    """
    if len(entities)>10:
        entities = entities[0:10]

    found_category, found_type = atp.classify_category(question)
    print(found_category,found_type)
    # if found_category == "resource":
    #     found_types = atp.classify_resource(question)[0:10]
    # else:
    #     found_types = [found_type]
    
    entities = ae.extend_entities(entities,found_category,found_type)

    # return jsonify(entities)
    answers = ae.answer_extractive(question,entities)
    
    response = {
        # "category":found_category,
        # "types":found_types[0],
        "answers":answers
    }

    return jsonify(response)

@app.route('/', methods=['GET'])
def greet():
    return "Usage: /answer?question=..."
