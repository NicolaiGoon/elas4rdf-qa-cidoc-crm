from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from boolean_question import BoolQ

model_name = "deepset/roberta-base-squad2"
# tokenizer = RobertaTokenizer.from_pretrained(model_name)
# model = RobertaForQuestionAnswering.from_pretrained(model_name)
device = "cpu"
print("Using Device: " + str(device))
pipeline = pipeline('question-answering',
                    model=model_name, tokenizer=model_name)

bq = BoolQ()

passage = """
3606 has type 300404670. Height has unit CM. Width has unit CM. Height has unit IN. Width has unit IN. Leonard Ochtman is composed of Leonard. Leonard Ochtman is composed of Ochtman. Leonard Ochtman has type 300404670. American has type 300379842. American? has type 300379842. Ochtman, Leonard has type sort_name. birth has time-span 1854. birth took place at Zonnemaire, Netherlands. death has time-span 1934. death took place at Cos Cob, Connecticut, United States. Leonard Ochtman is identified by 3606. Leonard Ochtman is identified by Leonard Ochtman. 30.25 has type Height. 76.835 has type Height. 102.235 has type Width. 40.25 has type Width. Leonard Ochtman is current or former member of American. Leonard Ochtman is current or former member of American?. Leonard Ochtman is identified by Ochtman, Leonard. 1909 begin of the begin 1909-01-01. 1909 end of the end 1909-12-31. Leonard Ochtman was brought into existence by birth. Leonard Ochtman was taken out of existence by death. 1909.11.2 has type 300404670. overall has dimension 30.25. overall has dimension 76.835. overall has dimension 102.235. overall has dimension 40.25. classification assigned Painting. production carried out by Leonard Ochtman. 18938 has type 300404621. Morning Haze has type 300404670. production has time-span 1909. Gift of William T. Evans has type 300026687. 30 1/8 x 40 1/8 in. (76.5 x 102.0 cm) has type 300266036. oil on canvas has type 300264237. classification had general purpose 300179869. Morning Haze is identified by 1909.11.2. Morning Haze has title Morning Haze. Morning Haze is identified by 18938. Morning Haze has type Painting. Morning Haze is composed of overall. Morning Haze has current owner Smithsonian American Art Museum. Morning Haze is referred to by Gift of William T. Evans. Morning Haze is referred to by 30 1/8 x 40 1/8 in. (76.5 x 102.0 cm). Morning Haze is referred to by oil on canvas. Morning Haze was classified by classification. Morning Haze was produced by production."""

question = "Was morning haze created by Leonard Ochtman?"


ans = pipeline(
    {"question": question, "context": passage})
print(ans)


# Predict the answer from the passage and the question
bq.tokenizer = pipeline.tokenizer
ans = bq.predict(passage, question)
print(ans)
print(bq.prediction_details())
