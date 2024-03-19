from gradio_client import Client

from src.question_answering.ApiAnswerExtraction import ApiAnswerExtraction


class Llama2(ApiAnswerExtraction):

    def __init__(self):
        self.prompt = "Answer a given question based on the context. Keep the answer as short as possible. You must always provide an answer."
        # question = "Was On the letter F of Flora given as a gift to the museum?"
        # passage = " On the letter F of Flora is identified by 1991.155.377. On the letter F of Flora is identified by 74320. On the letter F of Flora has type Drawing. On the letter F of Flora has title On the letter F of Flora. On the letter F of Flora has current owner Smithsonian American Art Museum. On the letter F of Flora is referred to by Gift of The Joseph and Robert Cornell Memorial Foundation. On the letter F of Flora is referred to by 9 x 7 in. (22.9 x 17.8 cm). On the letter F of Flora is referred to by drawing. On the letter F of Flora was produced by production. On the letter F of Flora was classified by classification"

        # self.client = Client("https://ysharma-explore-llamav2-with-tgi.hf.space/")

    def predict(self, question, passage):
        # self.client = Client("https://ysharma-explore-llamav2-with-tgi.hf.space/--replicas/9zqfs/")
        self.client = Client("https://huggingface-projects-llama-2-13b-chat.hf.space/--replicas/5c42d8wx6/")

        self.get_response(f"Context: {passage}")
        return self.get_response(f"Question: {question}")

    def extract_answer(self, question, passasge):
        return self.predict(question, passasge)

    def get_response(self, message):
        # return self.client.predict(
        #             message,	# str in 'Message' Textbox component
        #             self.prompt,	# str in 'Optional system prompt' Textbox component
        #             0.9,	# int | float (numeric value between 0.0 and 1.0)
        #                             # in 'Temperature' Slider component
        #             128,	# int | float (numeric value between 0 and 4096)
        #                             # in 'Max new tokens' Slider component
        #             0.6,	# int | float (numeric value between 0.0 and 1)
        #                             # in 'Top-p (nucleus sampling)' Slider component
        #             1.2,	# int | float (numeric value between 1.0 and 2.0)
        #                             # in 'Repetition penalty' Slider component
        #             api_name="/chat"
        return self.client.predict(
            message,  # str in 'Message' Textbox component
            self.prompt,  # str in 'Optional system prompt' Textbox component
            128,  # int | float (numeric value between 1 and 2048) in 'Max new tokens' Slider component
            0.6,  # int | float (numeric value between 0.1 and 4.0) in 'Temperature' Slider component
            0.9,  # int | float (numeric value between 0.05 and 1.0) in 'Top-p (nucleus sampling)' Slider component
            50,  # int | float (numeric value between 1 and 1000) in 'Top-k' Slider component
            1.2,  # int | float (numeric value between 1.0 and 2.0) in 'Repetition penalty' Slider component
            api_name="/chat"
        )
