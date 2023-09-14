import g4f

class gpt4():
    '''
    gpt4 api using extractive QA for boolean or Factoid questions
    '''

    def __init__(self):
        self.boolean_prompt = "You are a boolean answer extraction system, you answer with yes or no given a question and a passage. If the passage does not contain any useful information then the answer will be more probably no."

    def predict(self, question, passage):
        prompt = self.boolean_prompt
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "system", "content": prompt}, 
                      {"role":"user", "content": f"Question: {question} Passage: {passage}"}]
        )
        return response
