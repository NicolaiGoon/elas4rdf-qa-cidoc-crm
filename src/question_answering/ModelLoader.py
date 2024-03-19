from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline


class ModelLoader():

    def __init__(self, model_name):
        self.model_name = model_name

    def __download_model(self):
        model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        save_dir = "ae_models/" + self.model_name
        tokenizer.save_pretrained(save_dir)
        model.save_pretrained(save_dir)

    def __load_qa_model(self) -> AutoModelForQuestionAnswering:
        model = AutoModelForQuestionAnswering.from_pretrained("./ae_models/" + self.model_name)
        return model

    def __load_qa_tokenizer(self) -> AutoTokenizer:
        tokenizer = AutoTokenizer.from_pretrained("./ae_models/" + self.model_name)
        return tokenizer

    def get_qa_pipeline(self) -> pipeline:
        self.__download_model()
        model = self.__load_qa_model()
        tokenizer = self.__load_qa_tokenizer()
        qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)
        return qa_pipeline
