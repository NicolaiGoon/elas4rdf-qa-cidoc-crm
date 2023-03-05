FROM python:3.10.6

WORKDIR /usr/cidoc-qa

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install gunicorn==20.1.0

COPY . .

RUN chmod +x ./start-app.sh

RUN python -c "# Initalisation of pretrained extractive QA model\
        from transformers import (\
            RobertaForQuestionAnswering,\
            RobertaTokenizer,\
            QuestionAnsweringPipeline,\
        )\
        model_name = \"deepset/roberta-base-squad2\"\
        tokenizer = RobertaTokenizer.from_pretrained(model_name)\
        try:\
            model = RobertaForQuestionAnswering.from_pretrained(\"./resources/\" + model_name)\
        except:\
            model = RobertaForQuestionAnswering.from_pretrained(model_name)\
            # save model\
            print(\"saving model...\")\
            model.save_pretrained(\"./resources/\" + model_name)"

CMD ["./start-app.sh"]

EXPOSE 5000