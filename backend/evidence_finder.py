print('importing')
import os
from keywords import yake, rake, hybrid
from document import news_retriever
# from entailment.roberta import TransformerRobertaInferrer
from entailment.debertav3 import MyDeBERTAV3
from entailment import aggregator
from summarization import sentence_selector
from nlp_tools import utilities
from document.search_engine import SerpAPISearcher
from document.news_retriever import extract_multinews, retrieve_articles
from nlp_tools.vi_preprocess import vi_preprocessor
from nlp_tools.en_preprocess import en_preprocessor
# from nlp_tools.vin_translator import translate_vi2en, translate_en2vi
from config import SERP_API, DIFFBOT_API
# from config import NUM_PARALLEL_THREADS
# from multiprocessing import Pool
from langdetect import detect_langs, detect
import time
from tqdm import tqdm
import pickle
# import gensim.downloader
from nltk.corpus import wordnet
from collections import Counter
from nlp_tools import vin_translator
import string


# print('loading glove')
# glove_vectors = gensim.downloader.load('word2vec-google-news-300')


def synonym_extractor(phrase):
    synonyms = []

    for syn in wordnet.synsets(phrase):
        for l in syn.lemmas():
            synonyms.append(l.name())
    return synonyms


# def get_relevant_words(word):
#     close_words = glove_vectors.most_similar(word)
#     #     print('close_words = ', close_words)
#     synonyms = synonym_extractor(word)
#     synonyms = set([e.lower() for e in synonyms])
#     #     print('synonyms = ', synonyms)
#     relevant_words = []
#     for w, _ in close_words:
#         common_prefix = os.path.commonprefix([word, w])
#         if min(len(common_prefix) / len(w), len(common_prefix) / len(word)) >= 2 / 3:
#             relevant_words.append(w)
#         else:
#             if w.lower() in synonyms:
#                 relevant_words.append(w)
#     return relevant_words


# relevant_words = pickle.load(open('./resources/relevant_words.pkl', 'rb'))

searcher = SerpAPISearcher(api_key=SERP_API)
# roberta_inferrer = TransformerRobertaInferrer()
print('loading debertav3')
debertav3_inferrer = MyDeBERTAV3()


def extract_keywords(post, method='rake'):
    """
    extract keyword from post
    :param post:
    :param method:
    :return:
    """
    if method == 'yake':
        return yake.get_keywords(post)
    elif method == 'rake':
        return rake.get_keywords(post)
    elif method == 'hybrid':
        phrases, keywords, entities = hybrid.rake_pagerank(post, num_keywords=10, keyword_only=False)
        words = []
        for e in phrases:
            words.extend(e[0].split(' '))
        for e in keywords:
            words.append(e)
        for e in entities:
            words.append(e)
        words = dict(Counter(words))
        words = [(word, count) for word, count in words.items()]
        words.sort(key=lambda e: e[1], reverse=True)
        words = [e[0] for e in words[:5]]
        return words
    else:
        raise NotImplementedError("must be yake or rake or hybrid")


# def retrieve_articles(keywords):
#     """
#     to retrieve news articles relevant to keywords
#     :param keywords:
#     :return:
#     """
#     query = ' '.join(keywords)
#     urls = searcher.search(query=query)
#
#     articles = extract_multinews(urls)
#
#     articles = [e for e in articles if e['title'] != '' and e['content'] != '']
#     return articles


def process_article(param):
    article, post, keywords, method = param[0], param[1], param[2], param[3]
    recognizer = None
    if method == 'roberta':
        recognizer = roberta_inferrer
    else:
        # TODO: to be implemented
        pass
    relevant_sentences = utilities.get_relevant_sentence(article['content'], keywords)
    article['relevant_sentences'] = [{'text': s,
                                      'entailment': recognizer.infer_entailment(s, post)} for s in relevant_sentences]
    article['entailment'] = aggregator.aggregate(a['relevant_sentences'])


def infer_entailment(articles, post, keywords, method='debertav3'):
    """

    :param articles:
    :param keywords:
    :param post:
    :param method:
    :return:
    """
    print("inferring entailment")
    recognizer = None
    if method == 'debertav3':
        recognizer = debertav3_inferrer
    else:
        # TODO: to be implemented
        pass
    # print('in infer_entailment')
    print('finding relevant sentences')

    relevant_keywords = set(keywords)
    for keyword in keywords:
        # relevant_keywords.union(relevant_words.get(keyword, set()))
        # relevant_keywords = relevant_keywords.union(get_relevant_words(word=keyword))
        relevant_keywords = relevant_keywords.union(keyword.split('_'))

    print('relevant_keywords = ', relevant_keywords)
    sentences = []
    for a in tqdm(articles):
        relevant_sentences = [a['title']] + utilities.get_relevant_sentence(a['content'], relevant_keywords)
        lang = detect(a['title'])
        # print('relevant_sentences = ', relevant_sentences)
        a['relevant_sentences'] = len(relevant_sentences)
        sentences.extend([{'text': s, 'lang': lang} for s in relevant_sentences])

    print('recognizing entailment')
    entailment = recognizer.batch_infer([e['text'] for e in sentences], post)
    start_index = 0

    print('aggregating per article')
    for a in tqdm(articles):
        a['relevant_sentences'] = [{'text': sentences[i]['text'],
                                    'entailment': entailment[i]} for i in
                                   range(start_index, start_index + a['relevant_sentences'])]
        a['entailment'] = aggregator.aggregate(a['relevant_sentences'][0], a['relevant_sentences'][1:])
        start_index += len(a['relevant_sentences'])

    return articles
    # params = [(article, post, keywords, method) for article in articles]
    # with Pool(NUM_PARALLEL_THREADS) as p:
    #     p.map(process_article, params)
    # return articles


def summarize(articles):
    """

    :param articles:
    :return:
    """
    supporting_articles = [a for a in articles if a['entailment'] == 'entailment']
    refusing_articles = [a for a in articles if a['entailment'] == 'contradiction']
    evidences = {'support': sentence_selector.select(supporting_articles, entailment_label='entailment'),
                 'refuse': sentence_selector.select(refusing_articles, entailment_label='contradiction')}
    return evidences


def keyword_expansion(keywords, post):
    if post.count(' ') <= 10:
        post = post.translate(str.maketrans('', '', string.punctuation))
        keywords.extend([e for e in post.split(' ') if len(e) > 0])
    if post.count(' ') >= 3:
        if detect(post) != 'vi':
            post = vin_translator.translate_en2vi(post)
        else:
            post = vin_translator.translate_vi2en(post)
        post = post.translate(str.maketrans('', '', string.punctuation))
        keywords.extend([e for e in post.split(' ') if len(e) > 0])
    keywords = list(set(keywords))
    return keywords


def find_evidence(post, keywords=None, keyword_method='hybrid', entail_method='debertav3'):
    """

    :param post:
    :param keywords:
    :param keyword_method:
    :param entail_method:
    :return:
    """
    print('post = ', post)
    print('keywords = ', keywords)
    if keywords is None:
        print('extracting keywords')
        keywords = extract_keywords(post, method=keyword_method)

    # keywords = keyword_expansion(keywords, post)
    print('expanded keywords = ', keywords)
    print('retrieving articles')

    articles = retrieve_articles(keywords)

    # print('done retrieving articles')
    # result = detect_langs(post)
    # result = {e.lang: e.prob for e in result}
    # if result.get('en', 0) < 0.5:
    #     # post = utilities.google_translate(post, target_language='en')
    #     post = translate_vi2en(post)

    return summarize(infer_entailment(articles, post, keywords, method=entail_method))
