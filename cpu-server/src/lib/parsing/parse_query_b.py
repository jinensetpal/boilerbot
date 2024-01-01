from copy import deepcopy
import collections
import numpy as np
import json

from lib.parsing.keywords import *
from lib.const import *
from lib.utils import cleanup
from lib.remote_module.modules import classify_request, llm_parsing
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

# add included ingredients
def add_to_include(items, request):
    if request.get('ingredients'): request_ing_str_list = set(map(lambda ingredient: json.dumps(ingredient), request.get('ingredients')))
    else: request_ing_str_list = set()
    request_ing_str_list.update(list(map(lambda item: json.dumps({'name': item, 'excluded': False}), items)))
    request_ing_str_list.difference_update(list(map(lambda item: json.dumps({'name': item, 'excluded': True}), items)))
    request['ingredients'] = list(map(lambda ingredient: json.loads(ingredient), request_ing_str_list))

    print(f'Include ingredient B: {[*items]}')

    return request

# add excluded ingredients
def add_to_exclude(items, request):
    if request.get('ingredients'): request_ing_str_list = set(map(lambda ingredient: json.dumps(ingredient), request.get('ingredients')))
    else: request_ing_str_list = set()
    request_ing_str_list.update(list(map(lambda item: json.dumps({'name': item, 'excluded': True}), items)))
    request_ing_str_list.difference_update(list(map(lambda item: json.dumps({'name': item, 'excluded': False}), items)))
    request['ingredients'] = list(map(lambda ingredient: json.loads(ingredient), request_ing_str_list))

    print(f'Exclude ingredient B: {[*items]}')

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
                print(f'Include instrument B: {noun}')
            elif cates[i] == 'beverage':
                request['drinkName'] = noun
                print(f'Include drink B: {noun}')
    
    print(f'Action_Include B: {request}')

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
                print(f'Exclude instrument B: {noun}')
            elif cates[i] == 'beverage':
                if request.get('drinkName'): request_drink_str = request.get('drinkName')
                request_drink_str = request_drink_str.replace(noun, '')
                request['drinkName'] = request_drink_str
                print(f'Exclude drink B: {noun}')
                    
    
    print(f'Action_Exclude B: {request}')

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
                print(f'Remove ingredient B: {noun}')
            elif cates[i] == 'cooking instrument':
                if request.get('instrument'): request_instrument_list = set(request.get('instrument'))
                else: request_instrument_list = set()
                request_instrument_list.discard(noun)
                request['instrument'] = list(request_instrument_list)
                print(f'Remove instrument B: {noun}')
            elif cates[i] == 'beverage':
                if request.get('drinkName'): request_drink_str = request.get('drinkName')
                request_drink_str = request_drink_str.replace(noun, '')
                request['drinkName'] = request_drink_str
                print(f'Remove drink B: {noun}')
    
    print(f'Action_Remove B: {request}')

    return request

def parsing_diet(tokens, request):
    commands = tokens.intersection(KEYWORDS['diet_action'])
    if request.get('dietaryFilters'): request_diet_str_list = set([diet for diet in request.get('dietaryFilters')])
    else: request_diet_str_list = set()
    request_diet_str_list.update(list(map(lambda x: x.title(), commands)))
    request['dietaryFilters'] = list(request_diet_str_list)

    print(f'Action_Diet B: {request}')

    return request  

def parsing_mealtype(tokens, request):
    commands = tokens.intersection(KEYWORDS['mealtype_action'])
    mealtype = None

    if 'breakfast' in commands: mealtype = 'breakfast'
    if 'lunch' in commands: mealtype = 'lunch'
    if 'dinner' or 'supper' in commands: mealtype = 'dinner'
    if 'dessert' in commands: mealtype = 'dessert'
    request['mealType'] = mealtype

    print(f'Action_MealType B: {request}')

    return request    


def parse_action_b(state):
    text = getattr(state.current_state, 'text').lower()
    tokens = get_n_grams(text)
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    nav_action = False
    # edit_mode = getattr(state.user_attributes, 'edit_mode', False)
    responder = None

    search_request = getattr(state.user_attributes, text, None)
    if not search_request:
        search_request = deepcopy(DEFAULT_QUERY)
    else:
        new_request = deepcopy(DEFAULT_QUERY)
        new_request.update(search_request)
        search_request = new_request

    if not tokens.isdisjoint(KEYWORDS['back_action']) and curr_stage in {'QUERY_CONFIRM_RESPONDER', 'QUERY_EDIT_RESPONDER'}:

        nav_action = True
        edit_mode = False
        if curr_stage == 'QUERY_EDIT_RESPONDER': responder = 'QUERY_CONFIRM_RESPONDER'
        elif curr_stage == 'QUERY_CONFIRM_RESPONDER': responder = 'LAUNCH_RESPONDER'
    elif not tokens.isdisjoint(KEYWORDS['edit_action']) and curr_stage in {'QUERY_CONFIRM_RESPONDER'}:

        nav_action = True
        edit_mode = True
        responder = 'QUERY_EDIT_RESPONDER'
    elif not tokens.isdisjoint(KEYWORDS['submit_action']) and curr_stage in {'QUERY_CONFIRM_RESPONDER', 'QUERY_EDIT_RESPONDER'}:

        nav_action = True
        edit_mode = False
        responder = 'RECIPE_QUERY_RESPONDER'
    
    # search request parsing
    if not nav_action:
        if curr_stage in {'LAUNCH_RESPONDER', 'RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER', 'TASK_COMPLETE_RESPONDER'}:
            ingredients, parsed_query = llm_parsing(text, "recipe")
            search_request['dishName'] = parsed_query
            for item in ingredients:
                search_request['ingredients'].append({'name': item, 'excluded': False})
            
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
            setattr(state.user_attributes, 'search_request', search_request)
            if curr_stage == 'LAUNCH_RESPONDER':
                responder = 'QUERY_CONFIRM_RESPONDER'
            else:
                responder = 'QUERY_EDIT_RESPONDER'

    return responder
