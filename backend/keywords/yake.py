#  make use of YAKE for extracting keywords from a single text document
# YAKE: https://github.com/LIAAD/yake

import yake

file = open('./resources/english_stopwords.txt', 'r')
en_stopwords = []
for line in file:
    en_stopwords.append(line.strip())
file.close()
extractor = yake.KeywordExtractor(stopwords=set(en_stopwords))


def get_keywords(post, num_keywords=3):
    """
    make use of YAKE to extract keywords from post
    :param post: a string
    :param num_keywords: a int
    :return: list of strings, each string is a keywords
    """
    keywords = extractor.extract_keywords(post)
    keywords = [e[0] for e in keywords]
    return keywords[:num_keywords]
