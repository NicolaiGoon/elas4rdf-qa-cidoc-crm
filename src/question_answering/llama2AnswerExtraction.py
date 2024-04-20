from gradio_client import Client
from typing_extensions import deprecated

from src.question_answering.ApiAnswerExtraction import ApiAnswerExtraction


@deprecated("Please use TransformerAnswerExtractor instead")
class Llama2(ApiAnswerExtraction):

    def __init__(self):
        self.prompt = "Answer a given question based on the context. Keep the answer as short as possible. You must always provide an answer."

    def __predict(self, question, passage):
        # self.client = Client("https://ysharma-explore-llamav2-with-tgi.hf.space/--replicas/9zqfs/")
        self.client = Client("https://huggingface-projects-llama-2-13b-chat.hf.space/--replicas/5c42d8wx6/")

        self.__get_response(f"Context: {passage}")
        return self.__get_response(f"Question: {question}")

    def extract_answer(self, question, passage):
        return self.__predict(question, passage)

    def __get_response(self, message):
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
