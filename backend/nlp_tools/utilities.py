# from google.oauth2 import service_account
# from google.cloud import translate_v2 as translate
# from googletrans import Translator as FreeTranslator
# from config import TRANSLATION_CREDIT

from langdetect import detect_langs
from nlp_tools.en_preprocess import en_preprocessor
from nlp_tools.vi_preprocess import vi_preprocessor
import html


# credentials = service_account.Credentials.from_service_account_file(TRANSLATION_CREDIT)
# translate_client = translate.Client(credentials=credentials)


# free_translator = FreeTranslator()


def detect_languages(text):
    result = detect_langs(text)
    result = {e.lang: e.prob for e in result}
    return result


def is_en_or_vi(text):
    langs = detect_languages(text)
    if langs.get('en', 0) > 0.9:
        return True
    if langs.get('vi', 0) > 0.9:
        return True
    return False


def get_vi_stopwords():
    file = open('resources/vietnamese-stopwords-dash.txt', 'r')
    stopwords = [line.strip().lower() for line in file]
    file.close()
    return stopwords


def get_en_stopwords():
    file = open('resources/english_stopwords.txt', 'r')
    stopwords = [line.strip().lower() for line in file]
    file.close()
    return stopwords


# def api_based_translate(texts, target_language):
# def google_translate(texts, target_language):
#     if type(texts) == str:
#         result = translate_client.translate(texts, target_language=target_language, format_='html')
#         return html.unescape(result['translatedText'])
#     else:
#         result = translate_client.translate(values=texts, target_language=target_language, format_='html')
#         result = [html.unescape(e['translatedText']) for e in result]
#         return result


# def google_translate(texts, target_language):
#     # try:
#     print(texts)
#     translations = free_translator.translate(texts, dest=target_language)
#     return [e.text for e in translations]
#     # except:
#     #     # return api_based_translate(texts, target_language)
#     #     pass


def is_relevant(sentence, keywords):
    for keyword in keywords:
        if keyword in sentence.lower():
            return True
    return False


def relevant_score(sentence, relevant_keywords):
    sentence = sentence.lower()
    s = [1 for keyword in relevant_keywords if keyword in sentence]
    return sum(s)


def get_relevant_sentence(document, relevant_keywords, lang=None):
    """
    to extract sentences from a document that are relevant to a post
    :param document: list of string, each is a paragraph, i.e., containing multiple sentences
    :param relevant_keywords: string
    :return: list of strings, each is a relevant sentence
    """
    # TODO: to be implemented
    if lang is None:
        result = detect_languages(document)
        if result.get('en', 0) >= 0.9:
            lang = 'en'
        elif result.get('vi', 0) >= 0.9:
            lang = 'vi'
    # print('lang = ', lang)
    if lang is not None:
        if lang == 'en':
            sentences = en_preprocessor.sentence_split(document)
        elif lang == 'vi':
            sentences = vi_preprocessor.sentence_split(document)
        else:
            sentences = []
        # sentences = [sentence for sentence in sentences if is_relevant(sentence, keywords)]
        sentences = [(sentence, relevant_score(sentence, relevant_keywords)) for sentence in sentences]
        sentences.sort(key=lambda e: e[1], reverse=True)
        sentences = [e[0] for e in sentences[:3] if e[1] > 0]
        return sentences
    else:
        return []
