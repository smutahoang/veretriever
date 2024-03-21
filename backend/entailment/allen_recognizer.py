# make use of google translate API and Allen NLP's toolbox for entailment recognition
# Allen NLP toolbox: https://demo.allennlp.org/textual-entailment
from allennlp.predictors.predictor import Predictor
import allennlp_models.tagging
from langdetect import detect_langs
from nlp_tools import utilities


class AllenEntailmentInferrer:

    def __init__(self):
        self.predictor = Predictor.from_path("resources/mnli-roberta.2021-03-11.tar.gz")

    def infer_entailment(self, sent1, sent2):
        result = detect_langs(sent1)
        result = {e.lang: e.prob for e in result}
        if result.get('en', 0) < 0.5:
            sent1 = utilities.google_translate(sent1, target_language='en')

        result = detect_langs(sent2)
        result = {e.lang: e.prob for e in result}
        if result.get('en', 0) < 0.5:
            sent2 = utilities.google_translate(sent2, target_language='en')

        rs = self.predictor.predict(premise=sent1, hypothesis=sent2)

        return dict(zip(["entailment", "contradiction", "neutral"], rs["prob"]))
