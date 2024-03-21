def select(articles, entailment_label, top_k=5):
    """Select top_k relevant sentences given articles and label

    :param articles: list of articles
    :param top_k: number of selected sentences
    :param entailment_label:
    :return: top_k indices in the sentences list
    """
    rs = []
    for i in range(len(articles)):
        article = articles[i]
        rs.extend([(i, s) for s in article['relevant_sentences']])

    rs = sorted(rs, key=lambda x: x[1]["entailment"][entailment_label], reverse=True)
    rs = [articles[e[0]] for e in rs]

    for article in rs:
        article['relevant_sentences'].sort(key=lambda s: s['entailment'][entailment_label], reverse=True)
    selected_urls = set()
    selected_articles = []
    for article in rs:
        if article['url'] in selected_urls:
            continue
        selected_urls.add(article['url'])
        selected_articles.append({'title': article['title'],
                                  'url': article['url'],
                                  'notable_sentences': article['relevant_sentences']})

    return selected_articles[:top_k]
