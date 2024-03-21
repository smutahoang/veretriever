# VERetriever: Vietnamese-English Cross-lingual Online Evidence Retrieval for Combating Fake News

## Check out our [Online demo](http://veretriever.phapi.io:5500/)

## Introduction

A convenient and resource-free for Vietnamese-English cross-lingual online retrieval of news that support or oppose a statement

### Backend

* Download the [weight](https://drive.google.com/file/d/1wMmfn7tovu6kGfJ3RlDiH1fP40KCTrEM/view?usp=share_link) file and unzip it to <b>backend/pretrained</b>
* Install dependencies listed in <b>backend/requirements</b>
* From terminal, cd to <b>backend</b>, and run: <b>uvicorn run:app --port BACKEND_PORT</b>

### Frontend
* Modify this [line]() with backend's host address and port respectively
* Go to <b>frontend</b> and run <b>python -m http.server FRONTEND_PORT</b> from terminal


