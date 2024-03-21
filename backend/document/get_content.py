import re

from urllib.parse import urlparse
from bs4 import BeautifulSoup

from utilities.search_utils import get_html


class WebContent(object):
    """
    """
    def __init__(self):
        super(WebContent, self).__init__()
        self.title = None
        self.paragraph = None
        self.images = None

    def __repr__(self):
        list_ = ["WebContent(",
                 "title={}".format(self.title), "\n", " " * 11,
                 "paragraph={}..)".format(" ".join(self.paragraph[:2]))]

        return "".join(list_)


def get_news(url):
    """
    """
    html = get_html(url)
    if html:
        o = urlparse(url, "http")
        if "cnn.com" in o.netloc:
            return get_news_from_cnn(html)
        elif "nytimes.com" in o.netloc:
            return get_news_from_nytimes(html)
        elif "washingtonpost.com" in o.netloc:
            return get_news_from_wspost(html)
        elif "vnexpress.net" in o.netloc:
            return get_news_from_vnexpress(html)
        elif "dantri.com" in o.netloc:
            return get_news_from_dantri(html)
        elif "zing.vn" in o.netloc:
            return get_news_from_zing(html)
        else:
            raise NotImplementedError("Not supported")


def get_news_from_cnn(html):
    """
    """
    rs = WebContent()
    soup = BeautifulSoup(html, "lxml")
    if soup.find("h1", attrs={"class": "pg-headline"}):
        rs.title = soup.find("h1", attrs={"class": "pg-headline"}).text.strip()
    elif soup.find("h1", attrs={"class": "pg-headline"}):
        rs.title = soup.find("h1", attrs={"class": "Article__title"}).text.strip()
    else:
        rs.title = None
    rs.paragraph = [i.text.strip() for i in soup.findAll("div", attrs={"class": "zn-body__paragraph"}) if i.text.strip()]
    images = []
    for i in soup.findAll("img", attrs={"class": "media__image media__image--responsive"}):
        if i.parent.name == 'div':
            images.append(({"caption": i.get("alt"),
                            "url": i.get("data-src-full16x9").replace(r"//", "")}))
    rs.images = images

    return rs


def get_news_from_nytimes(html):
    """
    """
    rs = WebContent()
    soup = BeautifulSoup(html, "lxml")
    rs.title = soup.find("h1", attrs={"data-test-id": "headline"}).text.strip()
    rs.paragraph = [i.text.strip() for i in soup.findAll("p", attrs={"class": "css-axufdj evys1bk0"}) if i.text.strip()]
    images = []
    for i in soup.findAll("img"):
        if i.parent.name == "picture":
            images.append(({"caption": i.get("alt"),
                            "url": i.get("src")}))
    rs.images = images

    return rs


def get_news_from_wspost(html):
    """
    """
    rs = WebContent()
    soup = BeautifulSoup(html, "lxml")
    rs.title = soup.find("h1", attrs={"id": "main-content"}).text.strip()
    rs.paragraph = [re.sub(r'(“|”)', '"', i.text.strip()) for i in soup.findAll("p", attrs={"data-el": "text"}) if i.text.strip()]
    images = []
    for i in soup.select("div > img"):
        images.append({"caption": i.get("alt"),
                       "url": i.get("src").replace("&w=32", "&w=691")})
    rs.images = images

    return rs


def get_news_from_vnexpress(html):
    """
    """
    rs = WebContent()
    soup = BeautifulSoup(html, "lxml")
    rs.title = soup.find("h1", attrs={"class": "title-detail"}).text.strip()
    rs.paragraph = [i.text.strip() for i in soup.findAll("p", attrs={"class": "Normal", "style": False}) if i.text.strip()]
    images = []
    for i in soup.select("picture > source > img"):
        images.append({"caption": i.get("alt"),
                       "url": i.get("data-src").replace("&amp;", "&")})
    rs.images = images

    return rs


def get_news_from_dantri(html):
    """
    """
    rs = WebContent()
    soup = BeautifulSoup(html, "lxml")
    rs.title = soup.find("h1", class_="dt-news__title").text.strip()
    rs.paragraph = [i.text.strip() for i in soup.find("div", class_="dt-news__body").findAll("p", attrs={"style": False}) if i.text.strip()]
    images = []
    for i in soup.findAll("figure"):
        images.append({"caption": i.figcaption.text.strip(),
                       "url": i.img.get("data-original")})
    rs.images = images

    return rs


def get_news_from_zing(html):
    """
    """
    rs = WebContent()
    soup = BeautifulSoup(html, "lxml")
    rs.title = soup.find("h1", class_="the-article-title").text.strip()
    body = soup.find("div", class_="the-article-body")
    rs.paragraph = [i.text.strip() for i in body.findAll("p", attrs={"class": False}) if i.text.strip() and i.parent.name != "td"]
    images = []
    for i in body.findAll("table", class_="picture"):
        images.append({"caption": i.p.text,
                       "url": i.img.get("data-src")})
    rs.images = images

    return rs
