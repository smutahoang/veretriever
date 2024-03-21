from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import NMF

import json
import numpy as np


def decompose(docs, num_topics):
    # print('num_topics = ', num_topics)
    x = [doc['content'] for doc in docs]
    # print("x = ", x)
    vectorizer = CountVectorizer(min_df=5)
    tfidf_transformer = TfidfTransformer()
    bows = vectorizer.fit_transform(x)
    # print('bow done')
    # print(bows.sum(axis=1))
    tfidfs = tfidf_transformer.fit_transform(bows)
    # print(tfidfs.sum(axis=1))
    # print('tfidf done')
    print(np.isnan(bows.toarray()).any(), np.isnan(tfidfs.toarray()).any())

    model = NMF(n_components=num_topics,
                random_state=123456,
                # verbose=1,
                alpha=0.01,
                l1_ratio=0.5,
                init='nndsvd',
                max_iter=1000)
    doc_vectors = model.fit_transform(tfidfs)
    print('learning done')
    topic_vectors = model.components_
    vocab = vectorizer.get_feature_names()
    return doc_vectors, topic_vectors, vocab, vectorizer, tfidf_transformer


def get_top_topics(doc_vectors):
    weights = doc_vectors.mean(axis=0)
    indices = list(weights.argsort())
    indices.reverse()
    return [t for t in indices if weights[t] >= weights.mean()]


def get_top_words(t, topic_vectors, vocab, num_words=10):
    words = list(topic_vectors[t].argsort()[-num_words:])
    words.reverse()
    return [{'word': vocab[i], 'score': topic_vectors[t, i]} for i in words]


def get_top_docs(t, doc_vectors, num_docs=5):
    doc_indices = list(doc_vectors[:, t].argsort()[-num_docs:])
    doc_indices.reverse()
    return doc_indices
