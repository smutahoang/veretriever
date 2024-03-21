import os
import pickle

os.environ["TOKENIZERS_PARALLELISM"] = "false"
from typing import List, Optional

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
import torch
import evidence_finder
from keywords import rake, hybrid
from langdetect import detect_langs

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://0.0.0.0",
    "http://localhost:8080",
    "http://localhost:5500",
    "http://0.0.0.0:5500",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://54.254.238.216:5500",
    "http://eminer.phapi.io:5500",
    "http://veretriever.phapi.io:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

folder = os.path.dirname(__file__)
template_folder = os.path.join(folder, "templates")
static_folder = os.path.join(template_folder, "static")

app.mount("/static", StaticFiles(directory=static_folder), name="static")
templates = Jinja2Templates(directory=template_folder)


class KeywordExtractionRequest(BaseModel):
    post: str


class KeywordExtractionResponse(BaseModel):
    post: str
    keywords: Optional[List[str]] = None


class InvestigationRequest(BaseModel):
    post: str
    keywords: Optional[List[str]] = None


class Entailment(BaseModel):
    contradiction: float
    neutral: float
    entailment: float


class Sentence(BaseModel):
    text: str
    entailment: Entailment


class News(BaseModel):
    url: str
    title: str
    notable_sentences: Optional[List[Sentence]] = None


class Evidence(BaseModel):
    post: str
    keywords: List[str]
    support: Optional[List[News]] = None
    refuse: Optional[List[News]] = None


@app.post("/find_evidence", response_model=Evidence)
async def find_evidence(evidence_request: InvestigationRequest):
    post = evidence_request.post
    if evidence_request.keywords is not None and evidence_request.keywords != '':
        keywords = [keyword.lower() for keyword in evidence_request.keywords]
    else:
        # post = keyword_request.post
        # keywords = rake.get_keywords(post=post, lang=lang)
        keywords = hybrid.rake_pagerank(post=post, preprocessor=None, keyword_only=True)
        result = detect_langs(post)
        result = {e.lang: e.prob for e in result}
        if result.get('en', 0) < 0.5:
            lang = 'vi'
        else:
            lang = 'en'
        if lang == 'vi':
            keywords = [e.replace('_', ' ') for e in keywords]

    print('post = ', post)
    print('keywords = ', keywords)
    try:
        evidences = evidence_finder.find_evidence(post=post, keywords=keywords)
        return {
            'post': post,
            'keywords': keywords,
            'support': evidences['support'],
            'refuse': evidences['refuse']
        }
    except:
        return {
            'post': post,
            'keywords': keywords,
            'support': [],
            'refuse': []
        }


# @app.get("/", response_class=HTMLResponse)
# async def get_homepage(request: Request):
#     return templates.TemplateResponse("index.html", {'request': request, 'method': 'get'})
#
#
# @app.post("/", response_class=HTMLResponse)
# async def post_homepage(request: Request, post: str = Form(...), keywords: str = Form(...)):
#     try:
#         keywords = [key.strip() for key in keywords.split(',')]
#         evidences = evidence_finder.find_evidence(post=post, keywords=keywords)
#         data = {'post': post,
#                 'keywords': keywords,
#                 'support': evidences['support'],
#                 'refuse': evidences['refuse'],
#                 'request': request,
#                 'method': 'post'}
#         torch.cuda.empty_cache()
#         return templates.TemplateResponse("index.html", data)
#     except:
#         torch.cuda.empty_cache()


@app.post("/fake_find_evidence", response_model=Evidence)
async def fake_find_evidence(evidence_request: InvestigationRequest):
    post = 'Ăn tỏi có thể chữa được Covid'
    keywords = ['tỏi', 'chữa', 'covid']
    evidences = pickle.load(open('./toy_evidences.pkl', 'rb'))
    return {'post': post,
            'keywords': keywords,
            'support': evidences['support'],
            'refuse': evidences['refuse']
            }


@app.post("/extract_keywords", response_model=KeywordExtractionResponse)
async def extract_keywords(keyword_request: KeywordExtractionRequest):
    # async def fake_extract_keywords(keyword_request):
    print(keyword_request)
    post = keyword_request.post
    result = detect_langs(post)
    result = {e.lang: e.prob for e in result}
    if result.get('en', 0) < 0.5:
        lang = 'vi'
    else:
        lang = 'en'

    # keywords = rake.get_keywords(post=post, lang=lang)
    keywords = hybrid.rake_pagerank(text=post, preprocessor=None, keyword_only=True)
    if lang == 'vi':
        keywords = [e.replace('_', ' ') for e in keywords]
    return {'post': post,
            'keywords': keywords
            }


@app.post("/fake_extract_keywords", response_model=KeywordExtractionResponse)
async def fake_extract_keywords(keyword_request: KeywordExtractionRequest):
    # async def fake_extract_keywords(keyword_request):
    print(keyword_request)
    post = 'Ăn tỏi có thể chữa được Covid'
    keywords = ['tỏi', 'chữa', 'covid']
    return {'post': post,
            'keywords': keywords
            }
