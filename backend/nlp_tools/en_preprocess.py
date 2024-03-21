import re
from collections import Counter
import torch
import stanza

WEB_ADDRESS_RE = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

stanza.install_corenlp()
from stanza.server import CoreNLPClient


def extract_entities(annotated_sentence):
    print('annotated_sentence = ', annotated_sentence)
    entities = []
    entity = None
    entity_type = None
    for i in range(len(annotated_sentence)):
        annotated_word = annotated_sentence[i]
        if annotated_word['ner'] == 'O':
            if entity is not None:
                entities.append({'entity': entity, 'type': entity_type})
            entity = None
            entity_type = None
        else:
            if entity is None:
                entity = annotated_word['text']
                entity_type = annotated_word['ner']
            else:
                entity = f"{entity} {annotated_word['text']}"
    if entity is not None:
        entities.append({'entity': entity, 'type': entity_type})
    return entities


class EnPreprocessor:

    def __init__(self, use_gpu=False):
        # full_path = os.path.abspath('resources/VnCoreNLP-1.1.1.jar')
        # self.annotator = VnCoreNLP(full_path, annotators="wseg,pos,ner", max_heap_size='-Xmx2g')
        # self.annotator = stanza.Pipeline('en', processors='tokenize,pos,ner')
        self.annotator = stanza.Pipeline('en', processors='tokenize', use_gpu=use_gpu)

    def seg_pos(self, text):
        text = re.sub(WEB_ADDRESS_RE, ' ', text)
        texts = text.strip().split('\n')
        texts = [string for string in texts if string != ""]
        preprocessed_texts = []
        for p in texts:
            sentences = self.annotator(p).to_dict()
            preprocessed_texts.extend(sentences)
        seg_text = [' '.join([word['text'] for word in sentence]) for sentence in preprocessed_texts]
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
            doc = self.annotator(text)
            sentences.extend([sentence.text for sentence in doc.sentences])
        return sentences


class LightweightEnPreprocessor:

    def __init__(self):
        try:
            self.annotator = CoreNLPClient(
                annotators=['tokenize', 'ssplit', 'pos', 'ner'],
                timeout=30000,
                endpoint='http://localhost:17900',
                memory='6G')
        except:
            self.annotator = CoreNLPClient(
                annotators=['tokenize', 'ssplit', 'pos', 'ner'],
                timeout=30000,
                endpoint='http://localhost:17901',
                memory='6G')

    def seg_pos(self, text):
        text = re.sub(WEB_ADDRESS_RE, ' ', text)
        texts = text.strip().split('\n')
        texts = [string for string in texts if string != ""]

        preprocessed_texts = []
        seg_text = []

        for p in texts:
            sentences = self.annotator.annotate(p).sentence

            for sentence in sentences:
                tokens = sentence.token
                preprocessed_sentence = []
                for token in tokens:
                    word = {
                        'id': len(preprocessed_texts),
                        'text': token.word,
                        'start_char': token.beginChar,
                        'end_char': token.endChar,
                        'pos': token.pos,
                        'ner': token.ner
                    }
                    preprocessed_sentence.append(word)
                    seg_text.append(token.word)
                preprocessed_texts.append(preprocessed_sentence)
        seg_text = ' '.join(seg_text)
        entities = []
        for sentence in preprocessed_texts:
            entities.extend([e['entity'] for e in extract_entities(sentence)])
        print('entities =', entities)
        entities = dict(Counter(entities))

        return preprocessed_texts, seg_text, entities

    def sentence_split(self, text):
        text = re.sub(WEB_ADDRESS_RE, ' ', text)
        texts = text.strip().split('\n')
        texts = [string for string in texts if string != ""]
        sentences = []

        def get_original_sentence(text, sentence):
            return text[sentence.token[0].beginChar:sentence.token[-1].endChar]

        for text in texts:
            doc = self.annotator.annotate(text)
            sentences.extend([get_original_sentence(sentence=sentence, text=text) for sentence in doc.sentence])
        return sentences


# if torch.cuda.is_available():
#     en_preprocessor = EnPreprocessor(use_gpu=True)
# else:
#     en_preprocessor = EnPreprocessor(use_gpu=False)

en_preprocessor = LightweightEnPreprocessor()
