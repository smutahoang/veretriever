from keywords.rake import RakeKeywordExtractor
from keywords import graph
from nlp_tools.vi_preprocess import vi_preprocessor
from nlp_tools.en_preprocess import en_preprocessor
from nlp_tools import utilities


def rake_pagerank(text, preprocessor=None, keyword_only=True, num_keywords=3):
    langs = {e.lang: e.prob for e in utilities.detect_langs(text)}
    vi_prob = langs.get('vi', 0)
    if vi_prob >= 0.5:
        lang = 'vi'
    else:
        lang = 'en'

    if lang == 'vi':
        if preprocessor is None:
            preprocessor = vi_preprocessor
        stopwords = utilities.get_vi_stopwords()
    else:
        if preprocessor is None:
            preprocessor = en_preprocessor
        stopwords = utilities.get_en_stopwords()

    annotated_sentences, seg_sentence, entities = preprocessor.seg_pos(text)

    rk_extractor = RakeKeywordExtractor(preprocessor=preprocessor, lang=lang)
    phrases = rk_extractor.extract(seg_sentence, 50, preprocessed=True)
    _, keywords = graph.extract(annotated_sentences, stopwords, lang=lang, num_keywords=20)
    phrase_score = {}
    for phrase in phrases:
        words = phrase.split(' ')
        score = sum([keywords.get(word, 0) for word in words])
        phrase_score[phrase] = score / len(words)
    phrases = [(phrase, score) for phrase, score in phrase_score.items()]
    phrases.sort(key=lambda e: e[1], reverse=True)
    if keyword_only:
        keywords = [(k, v) for k, v in keywords.items()]
        keywords.sort(key=lambda e: e[1], reverse=True)
        return [e[0] for e in keywords][:num_keywords]
    else:
        return phrases, keywords, entities
