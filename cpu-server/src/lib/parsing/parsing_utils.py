from lib.parsing.keywords import *
from lib.remote_module.modules import classify_request


def get_step_ingredients(text):
    ing_list = []
    try:
        cates, probs, noun_phrases = classify_request(text)
        for i in range(len(cates)):
            if cates[i] == 'ingredient': ing_list.append(noun_phrases[i])
    except:
        print('Error in classify_request.')
    return ing_list

def parse_query(curr_task_domain, request, text):
    if curr_task_domain == 'COOK':
        text = text.replace('recipes', '').replace('recipe', '').replace('search', '').strip()
        terms = get_recipe_terms(text)
        if terms is None:
            return None
        dish_name, ingredients, drink_name, instrument_name = terms[0], terms[1], terms[2], terms[3]
        if ingredients:
            request['ingredients'] = ingredients
            request['dishName'] = ''
        if drink_name:
            request['drinkName'] = drink_name
            request['dishName'] = ''
        if instrument_name:
            request['instrument'] = instrument_name
            request['dishName'] = ''
        if dish_name:
            request['dishName'] = dish_name
        return request
    else:   # not in use
        words = text.split()
        elements = [item for item in words if item not in stopwords]
        if not elements: return None
        for element in elements:
            if any(entry['match']['articleTitle'] == element for entry in request['query']['bool']['must']):
                continue
            request['query']['bool']['must'].append({'match': {'articleTitle': str(element)}})
        return request


def get_recipe_terms(text):
    words = text.split()
    dish_name, dish_list, ing_list, drink, instrument = '', [], [], '', ''
    try:
        cates, probs, noun_phrases = classify_request(text)
    except:
        return None
    exclude_list, exclude = [], False

    for word in words:
        if word in ['no', 'not', 'without', 'don\'t']: exclude = True
        elif word in ['with', 'include']: exclude = False
        exclude_list.append(exclude)
    
    if cates is not None:   # request query clf
        for i in range(len(noun_phrases)):
            if cates[i] == 'beverage': drink = noun_phrases[i]
            elif cates[i] == 'dish': dish_list.append(noun_phrases[i])
            elif cates[i] == 'cooking instrument': instrument = noun_phrases[i]
            elif cates[i] == 'ingredient':
                idx = words.index(noun_phrases[i].split()[0])
                ing_list.append({'name': noun_phrases[i], 'excluded': exclude_list[idx]})
        
        # remove 'recipe'/'recipes' nouns
        matches = {word for word in dish_list if word in ['recipe', 'recipes']}
        filtered_dish_list = [word for word in dish_list if word not in matches]
        dish_name = ' '.join(filtered_dish_list)
    else:   # baseline keywords match
        seen = set()
        elements = [item for item in words if item not in stopwords]

        for word in words:
            if word in ingredients:
                ing_list.append({'name': word, 'excluded': exclude_list[words.index(word)]})
                seen.add(word)
            elif word in drinks:
                drink = word
                seen.add(word)
            elif word in instruments:
                instrument = word
                seen.add(word)
            elif word in elements:
                dish_list.append(word)
                seen.add(word)
        
        for element in elements:
            if element not in seen:
                dish_list.append(element)
        
        dish_name = ' '.join(dish_list) 
    return dish_name, ing_list, drink, instrument


def query_include(request, item):
    cates, probs, noun_phrases = classify_request(item)
    if cates is not None:   # request query clf
        if cates[0] == 'ingredient':
            if any(entry['name'] == noun_phrases[0] and entry['excluded'] == True for entry in request['ingredients']):
                idx = request['ingredients'].index({'name': noun_phrases[0], 'excluded': True})
                request['ingredients'][idx]['excluded'] = False
            elif not any(entry['name'] == noun_phrases[0] and entry['excluded'] == False for entry in request['ingredients']):
                request['ingredients'].append({'name': noun_phrases[0], 'excluded': False})
        elif cates[0] == 'cooking instrument':
            if noun_phrases[0] not in request['instrument']:
                request['instrument'] = noun_phrases[0]
        elif cates[0] == 'beverage':
            if noun_phrases[0] not in request['drinkName']:
                request['drinkName'] = noun_phrases[0]
    else:   # baseline keywords match
        if item in ingredients:
            if any(entry['name'] == item and entry['excluded'] == True for entry in request['ingredients']):
                idx = request['ingredients'].index({'name': item, 'excluded': True})
                request['ingredients'][idx]['excluded'] = False
            elif not any(entry['name'] == item and entry['excluded'] == False for entry in request['ingredients']):
                request['ingredients'].append({'name': item, 'excluded': False})
        elif item in instruments:
            if item not in request['instrument']:
                request['instrument'] = item
        elif item in drinks:
            if item not in request['drinkName']:
                request['drinkName'] = item
    return request

def query_exclude(request, item):
    cates, probs, noun_phrases = classify_request(item)
    if cates is not None:   # request query clf
        if cates[0] == 'ingredient':
            if any(entry['name'] == noun_phrases[0] and entry['excluded'] == False for entry in request['ingredients']):
                idx = request['ingredients'].index({'name': noun_phrases[0], 'excluded': False})
                request['ingredients'][idx]['excluded'] = True
            elif not any(entry['name'] == noun_phrases[0] and entry['excluded'] == True for entry in request['ingredients']):
                request['ingredients'].append({'name': noun_phrases[0], 'excluded': True})
        elif cates[0] == 'cooking instrument':
            if noun_phrases[0] in request['instrument']:
                request['instrument'].replace(noun_phrases[0], '')
        elif cates[0] == 'beverage':
            if noun_phrases[0] not in request['drinkName']:
                request['drinkName'].replace(noun_phrases[0], '')
    else:   # baseline keywords match
        if item in ingredients:
            if any(entry['name'] == item and entry['excluded'] == False for entry in request['ingredients']):
                idx = request['ingredients'].index({'name': item, 'excluded': False})
                request['ingredients'][idx]['excluded'] = True
            elif not any(entry['name'] == item and entry['excluded'] == True for entry in request['ingredients']):
                request['ingredients'].append({'name': item, 'excluded': True})
        elif item in instruments:
            if item in request['instrument']:
                request['instrument'].replace(item, '')
        elif item in drinks:
            if item not in request['drinkName']:
                request['drinkName'].replace(item, '')
    return request

def query_remove(request, item):
    cates, probs, noun_phrases = classify_request(item)
    if cates is not None:   # request query clf
        if cates[0] == 'ingredient':
            if any(entry['name'] == noun_phrases[0] and entry['excluded'] == False for entry in request['ingredients']):
                request['ingredients'].remove({'name': noun_phrases[0], 'excluded': False})
        elif cates[0] == 'cooking instrument':
            if noun_phrases[0] in request['instrument']:
                request['instrument'].replace(noun_phrases[0], '')
        elif cates[0] == 'beverage':
            if noun_phrases[0] not in request['drinkName']:
                request['drinkName'].replace(noun_phrases[0], '')
    else:   # baseline keywords match
        if item in ingredients:
            if any(entry['name'] == item and entry['excluded'] == False for entry in request['ingredients']):
                request['ingredients'].remove({'name': item, 'excluded': False})
        elif item in instruments:
            if item in request['instrument']:
                request['instrument'].replace(item, '')
        elif item in drinks:
            if item not in request['drinkName']:
                request['drinkName'].replace(item, '')
    return request

def query_diet(request, item):
    if item.title() not in request['dietaryFilters']:
        if item in {'vegan'}: item = 'vegetarian'
        request['dietaryFilters'].append(item.title())
    return request

def query_meal(request, item):
    if item.title() not in request['mealType']:
        request['mealType'] = item.title()
    return request


# computes the at most tri-grams
def get_n_grams(sentence):
    tokens = sentence.split(' ')
    rst = set()
    for n in range(4):
        rst.update([' '.join(item) for item in list(zip(*[tokens[i:] for i in range(n)]))])
    return rst


import numpy as np
import operator
import time
from thefuzz import fuzz
from lib.remote_module.modules import get_noun_phrases
# calculate fuzzy similarity between strings
def get_fuzzy_similarity(option_list, query):
    start = time.time()

    if not option_list: 
        end = time.time()
        print(f"Fuzzy Similarity Latency: {end - start}s")
        return '', 0

    values = [fuzz.token_sort_ratio(option, query) for option in option_list]
    mapping = dict(zip(option_list, values))
    title, ratio = max(mapping.items(), key=operator.itemgetter(1))
    # if ratio <= 70: title, ratio = get_distinct_similarity(option_list, query)
    if ratio == 0: title, ratio = '', 0

    print(f"Fuzzy title selection: {title}, Ratio: {ratio}")
    end = time.time()
    print(f"Fuzzy Similarity Latency: {end - start}s")
    return title, ratio

def get_distinct_similarity(option_list, query):
    start = time.time()

    common_tokens = list(set.intersection(*[set(get_nouns(option)) for option in option_list]))
    print(f"Common tokens: {common_tokens}")
    query_nouns = get_nouns(query)
    scores = []
    for option in option_list:
        option_nouns = get_nouns(option)
        if not option_nouns:
            scores.append(0)
        else:
            scores.append(len(np.intersect1d(np.setdiff1d(option_nouns, common_tokens), np.setdiff1d(query_nouns, common_tokens))) / len(option_nouns))

    mapping = dict(zip(option_list, list(map(lambda x: int(x * 100), scores))))
    title, ratio = max(mapping.items(), key=operator.itemgetter(1))

    end = time.time()
    print(f"Distinct Similarity Latency: {end - start}s")
    return title, ratio

def get_nouns(text):
    text = text.lower()
    nouns = get_noun_phrases(text)
    rst = []
    for noun in nouns:
        rst.extend(noun.split())
    print(rst)
    return rst
