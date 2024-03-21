# to determine entailment label between a document and a post by aggregating the labels
# between the document's sentences and the post
import numpy as np


def avg(sentences):
    """
    aggregating by simple averaging
    :param sentences:
    :return: dict
        {
            "entailment": mean of prob. value over all relevant sentences
            "neutral": ~
            "contradiction": ~
        }
    """
    rs = {"entailment": 0, "neutral": 0, "contradiction": 0}
    for sentence in sentences:
        for e, v in sentence['entailment'].items():
            rs[e] += v / len(sentences)
    return rs


def max_case(probabilities):
    cases = [(k, v) for k, v in probabilities.items()]
    cases.sort(key=lambda e: e[1], reverse=True)
    return cases[0][0]


def aggregate(title, sentences, method='avg'):
    """

    :param title:
    :param sentences:
    :param method:
    :return: either 'support', 'refuse', or 'not-determined'
    """
    title_entailment = max_case(probabilities=title['entailment'])
    if title_entailment != 'neutral':
        return title_entailment
    if len(sentences) == 0:
        return 'neutral'
    if method == 'avg':
        rs = avg(sentences[1:])
        if rs['entailment'] > 0:
            if rs['entailment'] > rs['contradiction']:
                return 'entailment'
            else:
                return 'contradiction'
        elif rs['contradiction'] > 0:
            if rs['contradiction'] > rs['entailment']:
                return 'contradiction'
            else:
                return 'entailment'
        else:
            return 'neutral'
        # return max(avg(sentences).items(), key=lambda x: x[1])[0]
    else:
        # TODO: to be implemented
        pass
