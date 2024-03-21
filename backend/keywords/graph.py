import networkx as nx
import string


def recover_sentence(annotated_sentence, lang='vi'):
    s = ''
    if lang == 'vi':
        postag = 'posTag'
        text_field = 'form'
    else:
        postag = 'pos'
        text_field = 'text'
    for w in annotated_sentence:
        if w[postag] == 'CH':
            s += w[text_field].replace('_', ' ')
        else:
            s += ' ' + w[text_field].replace('_', ' ')
    return s


def extract(annotated_sentences: list, stopwords, lang='vi', num_keysentences=1, num_keywords=5):
    g = nx.Graph()

    if lang == 'vi':
        postag = 'posTag'
        text_field = 'form'
        punct_tag = 'CH'
    else:
        postag = 'pos'
        text_field = 'text'
        punct_tag = 'PUNCT'  # does not work
    for s in range(len(annotated_sentences)):
        sentence = annotated_sentences[s]
        for w in sentence:
            if w[postag] != punct_tag:
                w = w[text_field].lower()
                if w not in stopwords and w not in string.punctuation:
                    g.add_edge(w, f'_s_{s}')
    h, a = nx.hits(g)
    sentence_scores = [(s, r) for s, r in a.items() if s.startswith('_s_')]
    word_scores = [(w, r) for w, r in a.items() if not w.startswith('_s_')]
    sentence_scores.sort(key=lambda e: e[1], reverse=True)
    word_scores.sort(key=lambda e: e[1], reverse=True)

    key_sentences = []
    for e in sentence_scores:
        s = e[0].split('_')[-1]
        s = int(s)
        key_sentences.append(recover_sentence(annotated_sentences[s], lang=lang))
        if len(key_sentences) == num_keysentences:
            break

    keywords = [e for e in word_scores[:min(num_keywords, len(word_scores))]]
    keywords = {e[0]: e[1] for e in keywords}
    return key_sentences, keywords
