from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class MyDeBERTAV3:

    def __init__(self, gpu_index=1):
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.tokenizer = AutoTokenizer.from_pretrained("MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
        self.model = AutoModelForSequenceClassification.from_pretrained('../eminer/pretrained/debertav3_hevenli')

        self.model.to(self.device)
        self.model.eval()

    def infer_entailment(self, sent1, sent2):
        with torch.no_grad():
            input = self.tokenizer(sent1, sent2, truncation=True, return_tensors="pt")
            output = self.model(input["input_ids"].to(self.device))  # device = "cuda:0" or "cpu"
            prediction = torch.softmax(output["logits"][0], -1).tolist()
        label_names = ["entailment", "neutral", "contradiction"]
        prediction = {name: pred for pred, name in zip(prediction, label_names)}
        return prediction

    def batch_infer(self, sent1s, sent2):
        with torch.no_grad():
            input = self.tokenizer(sent1s, [sent2] * len(sent1s), truncation=True, return_tensors="pt", padding=True,
                                   return_attention_mask=True)
            input["input_ids"] = input["input_ids"].to(self.device)
            input['attention_mask'] = input['attention_mask'].to(self.device)
            output = self.model(**input)  # device = "cuda:0" or "cpu"
            prediction = torch.softmax(output["logits"], -1).cpu().numpy()

        label_names = ["entailment", "neutral", "contradiction"]
        prediction = [{name: pred for pred, name in zip(pred, label_names)} for pred in prediction]
        return prediction


debertav3_inferrer = MyDeBERTAV3()


def get_relationship(text1, text2):
    return debertav3_inferrer.infer_entailment(text1, text2)
