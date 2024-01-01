from copy import deepcopy
import collections
import numpy as np
import json

from lib.parsing.keywords import *
from lib.const import *
from lib.remote_module.modules import classify_request
from lib.parsing.parsing_utils import get_n_grams, parse_query, query_include, query_exclude, query_remove, query_diet, query_meal
from lib.remote_module.modules import get_noun_phrases

KEYWORDS = {
    'back_action': {'previous', 'earlier', 'before', 'back', 'backward'},
    'include_action': {'add', 'include', 'with'},
    'exclude_action': {'exclude', 'no', 'without', 'don\'t', 'not'},
    'remove_action': {'remove'},
    'edit_action': {'edit', 'modify'},
    'submit_action': {'confirm', 'submit', 'continue', 'ok', 'yes', 'correct'},
    'diet_action': {'vegan', 'vegetarian', 'keto', 'gluten free', 'dairy free', 'high fiber', 'balanced'},
    'mealtype_action': {'breakfast', 'lunch', 'dinner', 'dessert'},
    'stopword': {'recipe', 'recipes', 'search', 'tutorial'}
}

THRESHOLD = 0.5

def trim_noun(noun):
    tokens = noun.split()
    diet_commons = np.intersect1d(tokens, [*KEYWORDS['diet_action']])
    mealtype_commons = np.intersect1d(tokens, [*KEYWORDS['mealtype_action']])
    stopword_commons = np.intersect1d(tokens, [*KEYWORDS['stopword']])

    tokens = np.setdiff1d(tokens, diet_commons)
    tokens = np.setdiff1d(tokens, mealtype_commons)
    tokens = np.setdiff1d(tokens, stopword_commons)

    return ' '.join(tokens)

def trim_request(request):
    for key, value in list(request.items()):
        if len(value) == 0:
            del request[key]
    return request


def parsing_query(text, request):
    words = [word.strip(',.') for word in text.split()]
    cates, probs, nouns = None, None, None
    try:
        cates, probs, nouns = classify_request(text)
    except:
        return request

    print(f"Classification results: Cates: {cates}, Probs: {probs}, Nouns: {nouns}")
    
    # get include/exclude list of tokens in F/T
    ie_list, excluded = [], False
    for word in words:
        if word in KEYWORDS['include_action']: excluded = False
        elif word in KEYWORDS['exclude_action']: excluded = True
        ie_list.append(excluded)

    include_list, exclude_list = set(), set()
    instrument_list, drink_str, dish_list = set(), '', []

    for i in range(len(cates)):
        noun = trim_noun(nouns[i])
        if len(noun) == 0:
            continue
        term = noun if len(noun.split()) == 1 else noun.split()[0]
        if term in reversed(words):
            last_idx = len(words) - list(reversed(words)).index(term) - 1
        else:
            continue
        if probs[i] <= THRESHOLD and cates[i] != 'dish':
            continue
        if cates[i] == 'ingredient':
            if not ie_list[last_idx]: include_list.add(noun)
            elif ie_list[last_idx]: exclude_list.add(noun)
        elif cates[i] == 'cooking instrument':
            if not ie_list[last_idx]: instrument_list.add(noun)
            elif ie_list[last_idx]: instrument_list.discard(noun)
        elif cates[i] == 'beverage':
            if not ie_list[last_idx]: drink_str = noun
            elif ie_list[last_idx]: drink_str = drink_str.replace(noun, '')
        elif cates[i] == 'dish':
            dish_list.append(noun)
                
    print(f"First Check Search Request: {str(request)}")

    # if no operations
    if len(include_list) == 0 and len(exclude_list) == 0 and len(instrument_list) == 0 and drink_str == '' and len(dish_list) == 0:
        return request
    
    # remove joints
    commons = np.intersect1d([*include_list], [*exclude_list])
    include_list = np.setdiff1d([*include_list], commons)
    exclude_list = np.setdiff1d([*exclude_list], commons)

    request = add_to_include(include_list, request)
    request = add_to_exclude(exclude_list, request)
    request['instrument'] = [*instrument_list]
    request['drinkName'] = drink_str
    request['dishName'] = ' '.join(dish_list)

    print(f'First query parsing: {request}')

    return request
    

# add included ingredients
def add_to_include(items, request):
    if request.get('ingredients'): request_ing_str_list = set(map(lambda ingredient: json.dumps(ingredient), request.get('ingredients')))
    else: request_ing_str_list = set()
    request_ing_str_list.update(list(map(lambda item: json.dumps({'name': item, 'excluded': False}), items)))
    request_ing_str_list.difference_update(list(map(lambda item: json.dumps({'name': item, 'excluded': True}), items)))
    request['ingredients'] = list(map(lambda ingredient: json.loads(ingredient), request_ing_str_list))

    print(f'Include ingredient: {[*items]}')

    return request

# add excluded ingredients
def add_to_exclude(items, request):
    if request.get('ingredients'): request_ing_str_list = set(map(lambda ingredient: json.dumps(ingredient), request.get('ingredients')))
    else: request_ing_str_list = set()
    request_ing_str_list.update(list(map(lambda item: json.dumps({'name': item, 'excluded': True}), items)))
    request_ing_str_list.difference_update(list(map(lambda item: json.dumps({'name': item, 'excluded': False}), items)))
    request['ingredients'] = list(map(lambda ingredient: json.loads(ingredient), request_ing_str_list))

    print(f'Exclude ingredient: {[*items]}')

    return request

# add item
def parsing_include(text, tokens, request):
    commands = tokens.intersection(KEYWORDS['include_action'])
    for command in commands:
        try:
            cates, probs, nouns = classify_request(text.partition(command)[2].strip())
        except:
            return request

        for i in range(len(cates)):
            noun = trim_noun(nouns[i])
            if probs[i] <= THRESHOLD:
                continue
            if cates[i] == 'ingredient':
                request = add_to_include([noun], request)
            elif cates[i] == 'cooking instrument':
                if request.get('instrument'): request_instrument_list = set(request.get('instrument'))
                else: request_instrument_list = set()
                request_instrument_list.add(noun)
                request['instrument'] = list(request_instrument_list)
                print(f'Include instrument: {noun}')
            elif cates[i] == 'beverage':
                request['drinkName'] = noun
                print(f'Include drink: {noun}')
    
    print(f'Action_Include: {request}')

    return request

# exclude item
def parsing_exclude(text, tokens, request):
    commands = tokens.intersection(KEYWORDS['exclude_action'])
    for command in commands:
        try:
            cates, probs, nouns = classify_request(text.partition(command)[2].strip())
        except:
            return request
        
        for i in range(len(cates)):
            noun = trim_noun(nouns[i])
            if probs[i] <= THRESHOLD:
                continue
            if cates[i] == 'ingredient':
                request = add_to_exclude([noun], request)
            elif cates[i] == 'cooking instrument':
                if request.get('instrument'): request_instrument_list = set(request.get('instrument'))
                else: request_instrument_list = set()
                request_instrument_list.discard(noun)
                request['instrument'] = list(request_instrument_list)
                print(f'Exclude instrument: {noun}')
            elif cates[i] == 'beverage':
                if request.get('drinkName'): request_drink_str = request.get('drinkName')
                request_drink_str = request_drink_str.replace(noun, '')
                request['drinkName'] = request_drink_str
                print(f'Exclude drink: {noun}')
                    
    
    print(f'Action_Exclude: {request}')

    return request

# remove item from include
def parsing_remove(text, tokens, request):
    commands = tokens.intersection(KEYWORDS['remove_action'])
    for command in commands:
        try:
            cates, probs, nouns = classify_request(text.partition(command)[2].strip())
        except:
            return request

        for i in range(len(cates)):
            noun = trim_noun(nouns[i])
            if probs[i] <= THRESHOLD:
                continue
            if cates[i] == 'ingredient':
                if request.get('ingredients'): request_ing_str_list = set(map(lambda ingredient: json.dumps(ingredient), request.get('ingredients')))
                else: request_ing_str_list = set()
                request_ing_str_list.discard(json.dumps({'name': noun, 'excluded': False}))
                request['ingredients'] = list(map(lambda ingredient: json.loads(ingredient), request_ing_str_list))
                print(f'Remove ingredient: {noun}')
            elif cates[i] == 'cooking instrument':
                if request.get('instrument'): request_instrument_list = set(request.get('instrument'))
                else: request_instrument_list = set()
                request_instrument_list.discard(noun)
                request['instrument'] = list(request_instrument_list)
                print(f'Remove instrument: {noun}')
            elif cates[i] == 'beverage':
                if request.get('drinkName'): request_drink_str = request.get('drinkName')
                request_drink_str = request_drink_str.replace(noun, '')
                request['drinkName'] = request_drink_str
                print(f'Remove drink: {noun}')
    
    print(f'Action_Remove: {request}')

    return request

def parsing_diet(tokens, request):
    commands = tokens.intersection(KEYWORDS['diet_action'])
    if request.get('dietaryFilters'): request_diet_str_list = set([diet for diet in request.get('dietaryFilters')])
    else: request_diet_str_list = set()
    request_diet_str_list.update(list(map(lambda x: x.title(), commands)))
    request['dietaryFilters'] = list(request_diet_str_list)

    print(f'Action_Diet: {request}')

    return request  

def parsing_mealtype(tokens, request):
    commands = tokens.intersection(KEYWORDS['mealtype_action'])
    mealtype = None

    if 'breakfast' in commands: mealtype = 'breakfast'
    if 'lunch' in commands: mealtype = 'lunch'
    if 'dinner' or 'supper' in commands: mealtype = 'dinner'
    if 'dessert' in commands: mealtype = 'dessert'
    request['mealType'] = mealtype

    print(f'Action_MealType: {request}')

    return request    


def parse_action(state):
    text = getattr(state.current_state, 'text').lower()
    tokens = get_n_grams(text)
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    nav_action = False
    # edit_mode = getattr(state.user_attributes, 'edit_mode', False)
    responder = None

    search_request = getattr(state.user_attributes, 'search_request', None)
    if not search_request:
        search_request = deepcopy(DEFAULT_QUERY)
    else:
        new_request = deepcopy(DEFAULT_QUERY)
        new_request.update(search_request)
        search_request = new_request

    # search request parsing
    if not nav_action:
        if curr_stage in {'LAUNCH_RESPONDER', 'RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER', 'TASK_COMPLETE_RESPONDER'}:
            search_request = parsing_query(text, search_request)
            
        if not tokens.isdisjoint(KEYWORDS['include_action']):
            search_request = parsing_include(text, tokens, search_request)

        if not tokens.isdisjoint(KEYWORDS['exclude_action']):
            search_request = parsing_exclude(text, tokens, search_request)

        if not tokens.isdisjoint(KEYWORDS['remove_action']):
            search_request = parsing_remove(text, tokens, search_request)

        if not tokens.isdisjoint(KEYWORDS['diet_action']):
            search_request = parsing_diet(tokens, search_request)

        if not tokens.isdisjoint(KEYWORDS['mealtype_action']):
            search_request = parsing_mealtype(tokens, search_request)

        if not search_request:
            cleanup(state)
            setattr(state.user_attributes, 'unsure', True)
            responder = 'LAUNCH_RESPONDER'
        else:
            setattr(state.user_attributes, 'search_request', text)
            responder = 'RECIPE_QUERY_RESPONDER'

    return responder
