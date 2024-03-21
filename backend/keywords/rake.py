from nlp_tools.vi_preprocess import vi_preprocessor
from nlp_tools.en_preprocess import en_preprocessor
from nlp_tools import utilities
from rake_nltk import Rake
from langdetect import detect_langs
import string


class RakeKeywordExtractor:
    def __init__(self, preprocessor=None, lang='vi'):
        if lang == 'vi':
            if preprocessor is None:
                self.preprocessor = vi_preprocessor
            else:
                self.preprocessor = preprocessor
            self.rake = Rake(stopwords=utilities.get_vi_stopwords(), punctuations=string.punctuation, min_length=1,
                             max_length=3)
        else:
            if preprocessor is None:
                self.preprocessor = en_preprocessor
            else:
                self.preprocessor = preprocessor
            self.rake = Rake(stopwords=utilities.get_en_stopwords(), punctuations=string.punctuation, min_length=1,
                             max_length=3)

    def extract(self, text, topk=50, preprocessed=False):
        if not preprocessed:
            _, text, _ = self.preprocessor.seg_pos(text)
        # print('text = ', text)
        self.rake.extract_keywords_from_text(text.lower())
        phrases = self.rake.get_ranked_phrases()
        return phrases[:min(topk, len(phrases))]


en_extractor = RakeKeywordExtractor(lang='en')
vi_extractor = RakeKeywordExtractor(lang='vi')


def get_keywords(post, lang='en'):
    if lang == 'en':
        return en_extractor.extract(post)
    else:
        return vi_extractor.extract(post)
