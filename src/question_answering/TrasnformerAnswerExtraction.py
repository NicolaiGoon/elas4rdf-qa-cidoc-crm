from src.question_answering.AnswerExtraction import AnswerExtraction
from src.question_answering.ModelLoader import ModelLoader


class TransformerAnswerExtraction(AnswerExtraction):

    def __init__(self, model_loader: ModelLoader):
        super().__init__()
        self.pipeline = model_loader.get_qa_pipeline()

    def extract_answer(self, question, passage) -> dict:
        return self.pipeline({"question": question, "context": passage})
