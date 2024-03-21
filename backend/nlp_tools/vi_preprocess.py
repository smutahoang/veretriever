import re
import os
from collections import Counter
from vncorenlp import VnCoreNLP
import underthesea
from underthesea import sent_tokenize
from config import VNCORENLP_ADDRESS, VNCORENLP_PORT

WEB_ADDRESS_RE = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"


def extract_entities(annotated_sentence, e_type=None):
    entities = []
    entity = None
    begin_marker = 'B-'
    in_marker = 'I-'
    if e_type is not None:
        begin_marker += e_type
        in_marker += e_type
    for word in annotated_sentence:
        if word.get('nerLabel', '').startswith(begin_marker):
            entity = word.get('form')
        elif word.get('nerLabel', '').startswith(in_marker):
            entity += ' ' + word.get('form')
        else:
            if entity is not None:
                entities.append(entity)
                entity = None
    if entity is not None:
        entities.append(entity)
    return entities


class ViPreprocessor:

    def __init__(self):
        # full_path = os.path.abspath('resources/VnCoreNLP-1.1.1.jar')
        # self.annotator = VnCoreNLP(full_path, annotators="wseg,pos,ner", max_heap_size='-Xmx2g')
        self.annotator = VnCoreNLP(address=VNCORENLP_ADDRESS, port=VNCORENLP_PORT)
        self.sentence_splitter = sent_tokenize

    def seg_pos(self, text):
        text = re.sub(WEB_ADDRESS_RE, ' ', text)
        texts = text.strip().split('\n')
        texts = [string for string in texts if string != ""]
        preprocessed_texts = []
        for p in texts:
            sentences = self.annotator.annotate(p)['sentences']
            preprocessed_texts.extend(sentences)
        seg_text = [' '.join([word['form'] for word in sentence]) for sentence in preprocessed_texts]
        seg_text = ' '.join(seg_text)
        entities = []
        for sentence in preprocessed_texts:
            entities.extend(extract_entities(sentence))
        entities = dict(Counter(entities))
        return preprocessed_texts, seg_text, entities

    def sentence_split(self, text):
        text = re.sub(WEB_ADDRESS_RE, ' ', text)
        texts = text.strip().split('\n')
        texts = [string for string in texts if string != ""]
        sentences = []
        for text in texts:
            sentences.extend(self.sentence_splitter(text))
        return sentences


vi_preprocessor = ViPreprocessor()
