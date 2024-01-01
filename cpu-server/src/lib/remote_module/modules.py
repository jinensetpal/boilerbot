import requests
import re
import time
import random

from lib.remote_module.remote_module_utils import *


def search_wikihow_db(query, top_k):
    """
    Search Query in Wikihow Vector DB
    Output: []
    """
    PARAMS = {
        'query_text': query, 
        'top_N': top_k, 
        'security_key': SEC_KEY
    }
    try:
        start = time.time()

        response = requests.post(url=WIKIHOW_DB_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        data = response.json().get('results')

        end = time.time()
        print(f"Search Wikihow DB: {end - start}s")
        return data
    except Exception as err:
        print(f'Failed to retrieve wikihow db: {err}')

def get_noun_phrases(query):
    """
    Get Noun Phrases from Query
    Output: []
    """
    PARAMS = {
        'query_text': query, 
        'security_key': SEC_KEY
    }
    try:
        start = time.time()

        response = requests.post(url=NOUN_PHRASES_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        data = response.json().get('results')

        end = time.time()
        print(f"Search Wikihow DB Latency: {end - start}s")
        return data
    except Exception as err:
        print(f'Failed to load get_noun_phrases: {err}')
        return []


def classify_request(query):
    """
    Classify Nouns into Ingredients/Instruments/Drinks
    Output: {'domain': [], 'probability': [], 'noun_phrases': []}
    """
    PARAMS = {
        'query_text': query, 
        'security_key': SEC_KEY
    }
    try:
        start = time.time()

        response = requests.post(url=REQUEST_CLF_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        data = response.json().get('results')
        end = time.time()
        
        if len(data) == 0:
            print(f"Classify Request Latency: {end - start}s")
            return None
        else: 
            print(f"Classify Request Result: {list(zip(data['domain'], data['probability'], data['noun_phrases']))}")
            print(f"Classify Request Latency: {end - start}s")
            return data['domain'], data['probability'], data['noun_phrases']
    except Exception as err:
        print(f'Failed to classify request: {err}')


def get_number(query):
    """
    Extract Number from Query
    Output: []
    """
    PARAMS = {
        'query_text': query, 
        'security_key': SEC_KEY
    }
    try:
        start = time.time()

        response = requests.post(url=GET_NUMBER_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        data = response.json().get('results')
        numbers = list(filter(lambda x: len(x) > 0, [re.findall(r'\d+', item) for item in data]))

        end = time.time()
        print(f"Get Number Latency: {end - start}s")
        return None if not numbers else int(numbers[0][0])
    except Exception as err:
        print(f'Failed to load get_number: {err}')
        return None


def get_special_event_db():
    """
    Special Event DB Access
    """
    PARAMS = {
        'security_key': SEC_KEY
    }
    try:
        start = time.time()

        response = requests.post(url=SPECIAL_EVENT_DB_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        data = response.json().get('results')

        end = time.time()
        print(f"Get Special Event DB Latency: {end - start}s")
        return data
    except Exception as err:
        print(f'Failed to retrieve special event db: {err}')


def write_log(text, bot_response, debug_info, conv_id):
    """
    Add Debug info to Log
    """
    PARAMS = {
        'text': text,
        'bot_response': bot_response,
        'debug_info': debug_info,
        'conversation_id': conv_id,
        'security_key': SEC_KEY
    }
    try:
        start = time.time()

        response = requests.post(url=ADD_LOG_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        print(f"Log conv_id: {conv_id}")
        print(f"Add Log Status: {response}")

        end = time.time()
        print(f"Add Log Latency: {end - start}s")
    except Exception as err:
        print(f'Failed to add log status: {err}')

# question classifier
def get_question_clf(query):
    """
    Classify if query is a statement or question
    For QA responder
    """
    PARAMS = {
        'security_key': SEC_KEY, 
        'query_text': query
    }
    try:
        start = time.time()

        response = requests.post(url=IS_QUESTION_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        data = response.json().get('results')

        end = time.time()
        print(f"Get Question CLF Latency: {end - start}s")
        return data
    except Exception as err:
        print(f'Failed to load get_question_clf: {err}')
        return False


def classify_domain(query, backup=False):
    """
    Classify the domain of user request
    Second layer of domain classification: differentiate from diy and chitchat
    """
    DOMAIN_LABELS = ['simple question and answering', 'chitchat', 'play music', 'other']
    if backup:
        DOMAIN_LABELS.extend(['cooking', 'diy', 'wikihow'])

    query = query.replace('how to ', '')

    PARAMS = {
        'text': query,
        'candidate_labels': DOMAIN_LABELS,
        'security_key': SEC_KEY
    }
    pred_label = 'unsure'
    try:
        start = time.time()

        response = requests.post(url=DOMAIN_CLF_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        data = response.json().get('results')
        pred_prob = max(data['scores'])
        if pred_prob > 0.5:
            pred_label = data['labels'][data['scores'].index(pred_prob)]

        print(f"Level 2 Domain Clf, Labels: {data['labels']}, Scores: {data['scores']}")
        if pred_label in ['diy', 'wikihow']:
            pred_label = 'DIY'
        elif pred_label == 'simple question and answering':
            pred_label = 'QUESTION'
        elif pred_label == 'cooking':
            pred_label = 'COOK'
        elif pred_label == 'play music':
            pred_label = 'UNSUPPORTED_COMMAND'
        else:
            pred_label = pred_label.upper()

        end = time.time()
        print(f"Level 2 Domain Clf Latency: {end - start}s")
        
        return pred_label, pred_prob
    except Exception as err:
        print(f'Failed to classify domain: {err}')
        return pred_label, 0

def search_recipes(query, top_k):
    """
    search for recipe from cobot api
    """
    print(f"Recipe search input: {query}")
    PARAMS = {
        'request': query,
        'top_N': top_k, 
        'security_key': SEC_KEY
    }
    try:
        response = requests.post(url=RECIPE_SEARCH_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"Failed to load Recipe Search Api: {err}")
        return None


def get_qa(query):
    """
    get qa from cobot evi
    """
    PARAMS = {
        "query": query,
        "security_key": SEC_KEY
    }
    try:
        response = requests.post(url=GET_QA_URL, json=PARAMS, timeout=1)
        response.raise_for_status()
        data = response.json().get('results')
        return data
    except Exception as err:
        print(f"Failed to load Recipe Search Api: {err}")
        return "Sorry, I didn't find anything related. Please ask me another question, hopefully about cooking or d.i.y."


# LLM APIs
def LLM_generate(prompts, max_len, temperature):
    PARAMS = {
        "security_key": SEC_KEY,
        "prompts": prompts,
        "max_new_tokens": max_len,
        "temperature": temperature
    }
    try:
        response = requests.post(url=LLM_URL, json=PARAMS, timeout=2)
        response.raise_for_status()
        data = response.json().get('result')
        return data
    except Exception as err:
        print(f"Failed to load LLM: {err}")

def build_recipe_prompt(q):
    # choose a random recipe prompt example
    recipe_prompt_example = random.choice(recipe_prompt_examples)
    complete_prompt = recipe_prompt_example + "user input: " + q + "\n\n### Response:\n"

    return complete_prompt

def build_wikihow_prompt(q):
    # choose a random wikihow prompt example
    wikihow_prompt_example = random.choice(wikihow_prompt_examples)
    complete_prompt = wikihow_prompt_example + "user input: " + q + "\n\n### Response:\n"

    return complete_prompt

def llm_parsing(q, q_type):
    complete_prompt = ""
    if q_type == "recipe":
        complete_prompt = build_recipe_prompt(q)
    else:
        complete_prompt = build_wikihow_prompt(q)
    
    res = LLM_generate([complete_prompt], 50, 0.55)
    res = res[0]["generated_text"]

    if q_type == "recipe":
        res = res.split("\n")
        
        ingredients = ""
        search_phrase = ""

        for line in res:
            if line.startswith("ingredients:") and ingredients == "":
                ingredients = line.replace("ingredients:", "").strip()
            elif line.startswith("search phrase:") and search_phrase == "":
                search_phrase = line.replace("search phrase:", "").strip()

        if ingredients == "" or ingredients == "none":
            ingredients = []
        else:
            if "," in ingredients:
                ingredients = ingredients.split(",")
                for i in range(len(ingredients)):
                    ingredients[i] = ingredients[i].strip()
            else:
                ingredients = [ingredients]
        
        print(f"LLM Recipe Parser: ingredients: {ingredients}, parsed phrase: {search_phrase}")
        return ingredients, search_phrase
    else:
        res = res.split("\n")
        search_phrase = ""

        for line in res:
            if line.startswith("search phrase:") and search_phrase == "":
                search_phrase = line.replace("search phrase:", "").strip()
                break

        print(f"LLM Wikihow Parser: {search_phrase}")
        return search_phrase
