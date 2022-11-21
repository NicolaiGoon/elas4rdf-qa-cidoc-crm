from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering, QuestionAnsweringPipeline
import entity_expansion as expansion

class AnswerExtraction:
    # This class contains methods for the answer extraction stage

    def __init__(self):
        # Initalisation of pretrained extractive QA model
        #model_name = "deepset/roberta-base-squad2"
        model_name = "distilbert-base-uncased-distilled-squad" 
        tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        model = DistilBertForQuestionAnswering.from_pretrained(model_name)
        self.pipeline = QuestionAnsweringPipeline(model=model,tokenizer=tokenizer,framework="pt",device=-1)
        
    def answer_extractive(self,question,entities):
        # Obtain a question from each given entity
        answers = []
        for e in entities:
            # print('ans '+e['uri'])
            # print(e)
            # emtpy text
            if e['text'] == '' or e['text'] == ' ':  
                answers.append({
                    'entity':e['uri'],
                    'answer':'',
                    'score':0,
                    'text':''
                    })
            else:
                output = self.pipeline(question,e['text'])
                # cant find answer
                if output == []:
                    answers.append({
                    'entity':e['uri'],
                    'answer':'',
                    'score':0,
                    'text':''
                    })
                else:
                    # highlighted_text = e['text'][0:output['start']]+'<b>'+e['text'][output['start']:output['end']]+'</b>'+e['text'][output['end']:] 
                    answers.append({
                        'entity':e['uri'],
                        'answer':output['answer'],
                        'score':round(output['score'],3),
                        'text':e['text']
                        })
        return sorted(answers, key=lambda k: k['score'],reverse=True) 

    def extend_entities(self,entities,category,atype,depth=2):
        # Extend entity descriptions with RDF nodes matching the answer type if it is not resource,
        # and if it is resource create text from a subgraph starting from the resource
        extended = []

        if(category=='resource' or (category == None and atype == None)):
            # type_uri = 'http://dbpedia.org/ontology/'+atype
            # sentences = expansion.resource_sentences(e['uri'],type_uri)
            return expansion.expandEntitiesPath(entities,depth)
        else:
            for e in entities:
                # print('ext '+e['uri'])
                sentences = set(expansion.literal_sentences(e['uri'],atype))
                new_text = (e['text'] + " " + ". ".join(sentences)).strip()
                # print(new_text)
                extended.append({
                    'uri':e['uri'],
                    'text':new_text
                    })
        return extended
