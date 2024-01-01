from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from src import const
import time
import json
from pydantic import BaseModel
from transformers import pipeline
from vectordb import search_vector_db
from spacy_parser import get_noun_phrases, get_number
from request_query_clf import handle_message
from intent_clf import predict_intent
from deberta import zero_shot_classification
from recipedb import search_vector_db as query_recipe
from cobot_qa import get_qa

class VectorDB_Query(BaseModel):
    query_text: str
    top_N: int
    security_key: str

class Noun_Phrase_Text(BaseModel):
    query_text: str
    security_key: str

class Request_Text(BaseModel):
    query_text: str
    security_key: str

class Question_Text(BaseModel):
    query_text: str
    security_key: str

class Number_text(BaseModel):
    query_text: str
    security_key: str

class Special_event(BaseModel):
    security_key: str

class Intent_Text(BaseModel):
    text: str
    security_key: str

class zero_shot(BaseModel):
    text: str
    candidate_labels: List[str]
    security_key: str

class recipe_query_input(BaseModel):
    request: str
    top_N: int
    security_key: str

class cobot_qa_input(BaseModel):
    query: str
    security_key: str


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

qclf = pipeline(model='shahrukhx01/question-vs-statement-classifier')

very_very_secret_key = 'insecure_placeholder'

@app.post('/')
async def health_check():
    return True

@app.post('/vectordb')
async def vectordb(VectorDB_Query: VectorDB_Query):
    if VectorDB_Query.security_key != very_very_secret_key:
        return {'error': 'security key is not correct'}

    start = time.time()

    res = search_vector_db(VectorDB_Query.query_text, VectorDB_Query.top_N)

    articles = []
    for file_name in res['ids'][0]:
        articles.append(json.load(open((const.DATA_DIR / 'wikihow' / f'{file_name}.json').as_posix()))['data'])

    end = time.time()
    print('found tutorial: ' + str(end - start))

    return {'results': articles}

@app.post('/noun_phrases')
async def noun_phrases(Noun_Phrase_Text: Noun_Phrase_Text):
    if Noun_Phrase_Text.security_key != very_very_secret_key:
        return {'error': 'security key is not correct'}

    start = time.time()

    noun_phrases = get_noun_phrases(Noun_Phrase_Text.query_text)

    end = time.time()
    print('found noun phrases: ' + str(end - start))

    return {'results': noun_phrases}

@app.post('/get_number')
async def get_num(Number_text: Number_text):
    if Number_text.security_key != very_very_secret_key:
        return {'error': 'security key is not correct'}

    start = time.time()

    number = get_number(Number_text.query_text)

    end = time.time()
    print('found number: ' + str(end - start))

    return {'results': number}


@app.post('/request_query')
async def request_query(Request_Text: Request_Text):

    if Request_Text.security_key != very_very_secret_key:
        return {'error': 'security key is not correct'}

    start = time.time()

    # go through the get_noun_phrases function first
    noung_phrases = get_noun_phrases(Request_Text.query_text)

    # check if noun_phrases is empty
    if len(noung_phrases) == 0:
        return {'results': []}

    # then go through the handle_message function
    res = handle_message(noung_phrases)

    end = time.time()
    print('request_clf: ' + str(end - start))

    return {'results': res}

@app.post('/question_clf')
async def question_clf(Question_Text: Question_Text):
    if Question_Text.security_key != very_very_secret_key:
        return {'error': 'security key is not correct'}

    start = time.time()

    clf = qclf(Question_Text.query_text)[0]['label'] == 'LABEL_1'

    end = time.time()
    print('classified question: ' + str(end - start))

    return {'results': clf}

@app.post('/intent_clf')
async def intent_clf(Intent_Text: Intent_Text):
    if Intent_Text.security_key != very_very_secret_key:
        return {'error': 'security key is not correct'}

    start = time.time()

    intent = predict_intent(Intent_Text.text)

    end = time.time()
    print('classified intent: ' + str(end - start))

    return {'results': intent}

@app.post('/zero_shot')
async def zero_shot_clf(zero_shot: zero_shot):
    if zero_shot.security_key != very_very_secret_key:
        return {'error': 'security key is not correct'}

    start = time.time()

    intent = zero_shot_classification(zero_shot.text, zero_shot.candidate_labels)

    end = time.time()
    print('classified intent: ' + str(end - start))

    return {'results': intent}

@app.post('/recipe_query')
async def recipe_query(recipe_query_input: recipe_query_input):
    if recipe_query_input.security_key != very_very_secret_key:
        return {'error': 'security key is not correct'}

    start = time.time()

    data = query_recipe(recipe_query_input.request, recipe_query_input.top_N)

    end = time.time()
    print('recipe response: ' + str(end - start))

    return {'documents': data}

@app.post('/cobot_qa')
async def cobot_qa_api(cobot_qa_input: cobot_qa_input):
    if cobot_qa_input.security_key != very_very_secret_key:
        return {'error': 'security key is not correct'}

    start = time.time()
    try:
        print(cobot_qa_input.query)
    except:
        print('could not print query')

    data = get_qa(cobot_qa_input.query)

    end = time.time()
    print('cobot qa response: ' + str(end - start))
    print(data)

    return {'results': data}

