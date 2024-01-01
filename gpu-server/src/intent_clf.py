from transformers import AutoTokenizer, AutoModelForSequenceClassification
from src import const
import pandas as pd
import random
import torch

id2label = {
	0: "BoilerBot.NextIntent", 
	1: "BoilerBot.StopIntent",
	2: "BoilerBot.CompleteIntent",
	3: "BoilerBot.PreviousIntent",
	4: "BoilerBot.SelectionIntent",
	5: "BoilerBot.UnknownIntent",
	6: "BoilerBot.MoreRecipesIntent",
	7: "BoilerBot.QAIntent",
	8: "BoilerBot.SearchTaskIntent"
}

label2id = dict((v, k) for k, v in id2label.items())

tokenizer = AutoTokenizer.from_pretrained((const.MODELS_DIR / "with-bot-intents-checkpoint-534/").as_posix())
model = AutoModelForSequenceClassification.from_pretrained((const.MODELS_DIR / "with-bot-intents-checkpoint-534/").as_posix())



def predict_intent(text):
	inputs = tokenizer(text, return_tensors="pt")
	with torch.no_grad():
		logits = model(**inputs).logits

	predicted_class_id = logits.argmax().item()

	return [predicted_class_id, model.config.id2label[predicted_class_id]]
