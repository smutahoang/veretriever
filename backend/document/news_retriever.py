from document import search_engine
from document.search_engine import SerpAPISearcher
from newspaper import Article
import requests
from tqdm import tqdm
from multiprocessing import Pool
from config import DIFFBOT_API, NUM_PARALLEL_THREADS, SERP_API
from nlp_tools import utilities
from newspaper import settings

settings.TOP_DIRECTORY = './tmp'


def search_articles(keywords, sources, engine='google', top_k=10):
    """
    make use of the search-engine to find news articles from sources that are relevant to keywords,
    and then extract the top-k links returned by the engine
    :param keywords: string, the keyword to search, e.g, "covid-19 cases"
    :param sources: list of strings, each is a source, i.e., a news channel, e.g., ["bbc.co.uk", "vnexpress.net"]
    :param engine: 'Google' or 'Bing', etc.
    :param top_k: number of top result to retrieve
    :return: list of top-k links return by the search engine
    """
    query = ' '.join(keywords)
    links = []
    for source in sources:
        # result[source] = [i.link for i in
        #                  search_engine.search(keyword, source, num=top_k, lang='en', engine=engine)]
        links.extend(search_engine.search(query=query, site=source, num=top_k, lang='en', engine=engine))
    return links


def extract_by_news3k(url):
    """
    download and extract the news article in the url
    :param url: string, link to a news article
        e.g., "https://vnexpress.net/ca-duong-tinh-sau-xuat-vien-lai-am-tinh-4192453.html"
    :return: dictionary, the extracted news article, including
        {
            "title": the title of the article
            "paragraphs": list of string, each is a paragraph
            "images": list of images included in the news
        }
    """
    try:
        article = Article(url)
        article.download()
        article.parse()

        return {'url': url, 'title': article.title, 'content': article.text, 'images': list(article.images)}
    except:
        return {'url': url, 'title': '', 'content': '', 'images': []}


def extract_by_diffbot(url):
    """
    download and extract the news article in the url
    :param url: string, link to a news article
        e.g., "https://vnexpress.net/ca-duong-tinh-sau-xuat-vien-lai-am-tinh-4192453.html"
    :return: dictionary, the extracted news article, including
        {
            "title": the title of the article
            "paragraphs": list of string, each is a paragraph
            "images": list of images included in the news
        }
    """
    try:
        result = requests.get(f'https://api.diffbot.com/v3/article?token={DIFFBOT_API}&url={url}', timeout=30)
        text = result.json()['objects'][0]['text']
        title = result.json()['objects'][0]['title']
        images = [e['url'] for e in result.json()['objects'][0]['images']]
        return {'url': url, 'title': title, 'content': text, 'images': images}
    except:
        return {'url': url, 'title': '', 'content': '', 'images': []}


def extract_news(url):
    result = extract_by_news3k(url)
    if result['content'] == '':
        return extract_by_diffbot(url)
    else:
        return result


def extract_multinews(urls):
    with Pool(NUM_PARALLEL_THREADS) as p:
        results = p.map(extract_news, urls)
    results = [e for e in results if e['content'] != '' and utilities.is_en_or_vi(e['content'])]
    return results


def retrieve(keywords, sources, engine='google', top_k=10):
    """
    make use of the search-engine to retrieve news articles from sources that are relevant to keywords
    :param keywords: list of strings, the keyword to search, e.g, "covid-19 cases"
    :param sources: list of strings, each is a source, i.e., a news channel, e.g., ["bbc.co.uk", "vnexpress.net"]
    :param engine: 'Google' or 'Bing', etc.
    :param top_k: number of top result to retrieve for each keyword
    :return: dictionary, the extracted news article, including
        {
            "url": url to the article,
            "title": the title of the article,
            "paragraphs": list of string, each is a paragraph,
            "images": list of images included in the news
        }
    """
    urls = search_articles(keywords, sources, engine=engine, top_k=top_k)
    urls = set(urls)
    articles = [extract_by_news3k(url) for url in urls]
    return articles


searcher = SerpAPISearcher(api_key=SERP_API)


def retrieve_articles(keywords):
    """
    to retrieve news articles relevant to keywords
    :param keywords:
    :return:
    """
    query = ' '.join(keywords)
    urls = searcher.search(query=query)
    print('#urls = ', len(urls))
    # articles = extract_multinews(urls)

    articles = []
    for url in tqdm(urls):
        articles.append(extract_news(url))
    articles = [e for e in articles if e['content'] != '' and utilities.is_en_or_vi(e['content'])]
    articles = [e for e in articles if e['title'] != '' and e['content'] != '']
    return articles
