import torch
from langdetect import detect_langs
from nlp_tools import utilities
from nlp_tools.vin_translator import translate_vi2en, tokenizer_en2vi, batch_translate_vi2en
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class TransformerRobertaInferrer:

    def __init__(self, gpu_index=1):
        self.tokenizer = AutoTokenizer.from_pretrained("roberta-large-mnli")
        self.model = AutoModelForSequenceClassification.from_pretrained("roberta-large-mnli")
        self.device = torch.device(f"cuda:{gpu_index}" if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()

    def infer_entailment(self, sent1, sent2):
        # print(sent1, sent2)
        detect_lang_time = 0
        translate_time = 0
        start = time.perf_counter()
        result = detect_langs(sent1)
        result = {e.lang: e.prob for e in result}
        end = time.perf_counter()
        detect_lang_time += end - start
        if result.get('en', 0) < 0.5:
            start = time.perf_counter()
            # sent1 = utilities.google_translate(sent1, target_language='en')
            sent1 = translate_vi2en(sent1)
            end = time.perf_counter()
            translate_time += end - start

        start = time.perf_counter()
        result = detect_langs(sent2)
        result = {e.lang: e.prob for e in result}
        end = time.perf_counter()
        detect_lang_time += end - start
        if result.get('en', 0) < 0.5:
            start = time.perf_counter()
            # sent2 = utilities.google_translate(sent2, target_language='en')
            sent2 = translate_vi2en(sent2)
            end = time.perf_counter()
            translate_time += end - start

        print(sent1, sent2)
        start = time.perf_counter()
        encoded_pair = self.tokenizer(sent1, sent2,
                                      padding='max_length',  # Pad to max_length
                                      truncation=True,  # Truncate to max_length
                                      max_length=128,
                                      return_tensors='pt')  # Return torch.Tensor object

        with torch.no_grad():
            prediction = self.model(encoded_pair['input_ids'].to(self.device))
            logits = prediction.logits
            probabilities = torch.softmax(logits, dim=1).cpu().detach().numpy()[0]
        end = time.perf_counter()
        predict_time = end - start
        print(detect_lang_time, translate_time, predict_time)
        return dict(zip(["contradiction", "neutral", "entailment"], probabilities))

    def batch_infer(self, sent1s, sent2):
        # print(sent1, sent2)
        translate_time = 0
        start = time.perf_counter()
        to_translate = []
        for i in range(len(sent1s)):
            sent1 = sent1s[i]['text']
            lang = sent1s[i].get('lang', None)
            if lang != 'en':
                to_translate.append(sent1)
        # trans = utilities.google_translate(to_translate, target_language='en')
        trans = batch_translate_vi2en(to_translate)
        batch = []
        j = 0
        for i in range(len(sent1s)):
            sent1 = sent1s[i]['text']
            lang = sent1s[i].get('lang', None)
            if lang != 'en':
                batch.append(trans[j])
                j += 1
            else:
                batch.append(sent1)

        result = detect_langs(sent2)
        result = {e.lang: e.prob for e in result}
        if result.get('en', 0) < 0.5:
            # sent2 = utilities.google_translate(sent2, target_language='en')
            sent2 = translate_vi2en(sent2)
        end = time.perf_counter()
        translate_time += end - start

        # print(sent1, sent2)
        start = time.perf_counter()
        with torch.no_grad():
            encoded_pair = self.tokenizer(batch, [sent2] * len(sent1s),
                                          padding='max_length',  # Pad to max_length
                                          truncation=True,  # Truncate to max_length
                                          max_length=128,
                                          return_tensors='pt')  # Return torch.Tensor object

            prediction = self.model(encoded_pair['input_ids'].to(self.device))
            logits = prediction.logits
            probabilities = torch.softmax(logits, dim=1).cpu().detach().numpy()
        end = time.perf_counter()
        predict_time = end - start
        print('-- computing time: ', translate_time, predict_time)
        return [dict(zip(["contradiction", "neutral", "entailment"], probabilities[i])) for i in range(len(sent1s))]


# roberta_inferrer = FairSeqRobertaInferrer()

roberta_inferrer = TransformerRobertaInferrer()


def get_relationship(text1, text2):
    return roberta_inferrer.infer_entailment(text1, text2)
