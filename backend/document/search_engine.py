from __future__ import unicode_literals
from __future__ import absolute_import

from serpapi import GoogleSearch
from builtins import object
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from unidecode import unidecode
from config import INFORMATION_SOURCES


# from utilities.search_utils import get_search_url, get_html
#
#
# class SearchResult(object):
#     """Represents a google/bing search result.
#     """
#
#     def __init__(self):
#         self.name = None  # The title of the link
#         self.link = None  # The external link
#         self.description = None  # The description of the link
#
#     def __repr__(self):
#         name = self._limit_str_size(self.name, 55)
#         description = self._limit_str_size(self.description, 49)
#
#         list_google = ["SearchResult(",
#                        "name={}".format(name), "\n", " " * 13,
#                        "description={}".format(description)]
#
#         return "".join(list_google)
#
#     def _limit_str_size(self, str_element, size_limit):
#         """Limit the characters of the string, adding .. at the end."""
#         if not str_element:
#             return None
#
#         elif len(str_element) > size_limit:
#             return unidecode(str_element[:size_limit]) + ".."
#
#         else:
#             return unidecode(str_element)
#
#
# def get_all_links(html):
#     # print('html = ', html)
#     soup = BeautifulSoup(html, features="lxml")
#     links = [a['href'] for a in soup.find_all('a', href=True)]
#     links = [link for link in links if '\\' not in link]
#     links = [link[:link.find('#')] if '#' in link else link for link in links]
#     links = [link[:link.find('%')] if '%' in link else link for link in links]
#     links = [link[:link.find('@')] if '@' in link else link for link in links]
#     return links
#
#
# def search(query, site=None, num=10, lang='en', engine='google'):
#     """Returns a list of SearchResult.
#
#     Args:
#         query: String to search
#         site: search in a specific domain
#         num: number of results in a page
#         lang : language of the document
#         engine : search engine (google/bing)
#
#     Returns:
#         Result object."""
#
#     url = get_search_url(query, site=site, num=num, lang=lang, search_engine=engine)
#     print('search url = ', url)
#     html = get_html(url)
#     # print('html = ', html)
#     if site is not None:
#         sites = [site]
#         if not site.startswith('www'):
#             sites.append('www.' + site)
#
#         if html is not None:
#             # soup = BeautifulSoup(html, "lxml")
#             # if engine == 'google':
#             #     r = soup.findAll("div", attrs={"class": "g"})
#             # elif engine == 'bing':
#             #     r = soup.findAll("li", attrs={"class": "b_algo"})
#             # # print('r = ', r)
#             # for li in r:
#             #     res = SearchResult()
#             #     res.name = _get_name(li, engine)
#             #     res.link = _get_link(li, engine)
#             #     res.description = _get_description(li, engine)
#             #
#             #     results.append(res)
#             links = get_all_links(html)
#             # print('links = ', links)
#             # print(len(links))
#             links = [link for link in links if urlparse(link).netloc in sites]
#             # print('after filtering by domain links = ', links)
#             # print(len(links))
#             # links = [link for link in links if link_validator.is_article_link_domain(link, domain)]
#             # print('after selection: ', links)
#             # print(len(links))
#             return links
#     else:
#         if html is not None:
#             soup = BeautifulSoup(html, "lxml")
#             if engine == 'google':
#                 r = soup.findAll("div", attrs={"class": "g"})
#             elif engine == 'bing':
#                 r = soup.findAll("li", attrs={"class": "b_algo"})
#             print('r = ', r)
#             links = []
#             for li in r:
#                 links.append(_get_link(li, engine))
#             return links
#     return []
#
#
# def _get_name(li, engine):
#     """Return the name of a search."""
#     a = li.find("a")
#     if a is not None:
#         return a.text.strip()
#     return None
#
#
# def _get_link(li, engine):
#     """Return external link from a search."""
#     try:
#         a = li.find("a")
#         link = a["href"]
#     except Exception:
#         return None
#     return _filter_link(link)
#
#
# def _get_description(li, engine):
#     """Return the description of a google/bing search.
#     """
#     if engine == "google":
#         sdiv = li.find("div", attrs={"class": "IsZvec"})
#         if sdiv:
#             stspan = sdiv.find("span", attrs={"class": "aCOpRe"})
#             if stspan is not None:
#                 return stspan.text.strip()
#     elif engine == "bing":
#         desc = li.find("p")
#         if desc is not None:
#             return desc.getText().strip()
#     else:
#         return None
#
#
# def _filter_link(link):
#     '''Filter links found in the Google/Bing result pages HTML code.
#     Returns None if the link doesn't yield a valid result.
#     '''
#     try:
#         o = urlparse(link, 'http')
#         # link type-1
#         # "https://www.gitbook.com/book/ljalphabeta/python-"
#         if o.netloc and 'google' not in o.netloc:
#             return link
#         # link type-2
#         # "http://www.google.com/url?url=http://python.jobbole.com/84108/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwj3quDH-Y7UAhWG6oMKHdQ-BQMQFggUMAA&usg=AFQjCNHPws5Buru5Z71wooRLHT6mpvnZlA"
#         if o.netloc and o.path.startswith('/url'):
#             try:
#                 link = parse_qs(o.query)['url'][0]
#                 o = urlparse(link, 'http')
#                 if o.netloc and 'google' not in o.netloc:
#                     return link
#             except KeyError:
#                 pass
#         # Decode hidden URLs.
#         if link.startswith('/url?'):
#             try:
#                 # link type-3
#                 # "/url?q=http://python.jobbole.com/84108/&sa=U&ved=0ahUKEwjFw6Txg4_UAhVI5IMKHfqVAykQFggUMAA&usg=AFQjCNFOTLpmpfqctpIn0sAfaj5U5gAU9A"
#                 link = parse_qs(o.query)['q'][0]
#                 # Valid results are absolute URLs not pointing to a Google domain
#                 # like images.google.com or googleusercontent.com
#                 o = urlparse(link, 'http')
#                 if o.netloc and 'google' not in o.netloc:
#                     return link
#             except KeyError:
#                 # link type-4
#                 # "/url?url=https://machine-learning-python.kspax.io/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwj3quDH-Y7UAhWG6oMKHdQ-BQMQFggfMAI&usg=AFQjCNEfkUI0RP_RlwD3eI22rSfqbYM_nA"
#                 link = parse_qs(o.query)['url'][0]
#                 o = urlparse(link, 'http')
#                 if o.netloc and 'google' not in o.netloc:
#                     return link
#
#     # Otherwise, or on error, return None.
#     except Exception:
#         pass
#     return None


def prepare_query(query):
    query += ' ' + ' OR '.join([f'site:{e}' for e in INFORMATION_SOURCES])
    return query


class SerpAPISearcher:
    def __init__(self, api_key):
        self.api_key = api_key

    def vi_search(self, query):
        params = {
            "api_key": self.api_key,
            "engine": "google",
            "q": query,
            "google_domain": "google.com.vn",
            "gl": "vn",
            "hl": "vi",
            "tbm": "nws",
            "num": "20"
        }

        searcher = GoogleSearch(params)
        results = searcher.get_dict()
        return results

    def en_search(self, query):
        params = {
            "api_key": self.api_key,
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "tbm": "nws",
            "num": "20"
        }

        searcher = GoogleSearch(params)
        results = searcher.get_dict()
        return results

    def search(self, query):
        result = self.en_search(query=query)
        # print('en_search result = ', result)
        urls = [e['link'] for e in result['news_results']]
        result = self.vi_search(query=query)
        # print('vi_search result = ', result)
        urls.extend([e['link'] for e in result['news_results']])
        return list(set(urls))


if __name__ == "__main__":
    for i in search("Covid tại Việt Nam 2021", num=10, lang='vi', engine='google'):
        print(i.link)
