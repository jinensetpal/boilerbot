import requests
import time
import random
# import json

def test_sbert():
    url = 'http://127.0.0.1:8000/sbert'
    x = requests.post(url, json=['This is an example sentence', 'Each sentence is converted'])
    print(x.text)

def generateRandomQuery():
	# genrate a random int between 0 and 1
	rnd_int = 0

	# part one of the query: phrases like "how to", "how do I"...
	query_starters = ["how to", "how do I", "how can I", "I want to", "help me", "I want to know how to", "do you know how can I", "", "", "", "", "", "", "", ""]

	# part two of the query: a random verb and a random noun phrase
	if rnd_int == 0:
		# the verbs should be for cooking
		query_verbs = ["cook", "make", "prepare"]
		query_noun_phrases = ["cake", "pizza", "fries", "fried chicken", "BBQ steak", "salad", "fish", "pasta", "soup", "sushi", "ramen", "sandwich", "burger", "hot dog", "chicken nuggets", "chicken wings", "chicken tenders", "chicken strips", "chicken sandwich", "chicken salad", "chicken soup", "chicken pasta", "chicken pizza", "chicken burger", "chicken hot dog", "chicken fries", "chicken fried chicken", "chicken fried steak", "chicken fried rice", "chicken fried fish", "chicken fried nuggets", "chicken fried wings", "chicken fried tenders", "chicken fried strips", "chicken fried sandwich", "chicken fried salad", "chicken fried soup", "chicken fried pasta", "chicken fried pizza", "chicken fried burger", "chicken fried hot dog", "chicken fried fries", "chicken fried nuggets", "chicken fried wings", "chicken fried tenders", "chicken fried strips", "chicken fried sandwich", "chicken fried salad", "chicken fried soup", "chicken fried pasta", "chicken fried pizza", "chicken fried burger", "chicken fried hot dog", "chicken fried fries", "pork", "beef", "steak", "fish", "rice", "noodles", "vegetables", "chicken", "pork chops", "pork ribs", "pork steak", "pork fish", "pork rice", "pork noodles", "pork vegetables", "pork chicken", "beef chops", "beef ribs", "beef steak", "beef fish", "beef rice", "beef noodles", "beef vegetables", "beef chicken", "steak chops", "steak ribs", "steak steak", "steak fish", "steak rice", "steak noodles", "steak vegetables", "steak chicken", "fish chops", "fish ribs", "fish steak", "fish fish", "fish rice", "fish noodles", "fish vegetables", "fish chicken", "rice chops", "rice ribs", "rice steak", "rice fish", "rice rice", "rice noodles", "rice vegetables", "rice chicken", "noodles chops", "noodles ribs", "noodles steak", "noodles fish", "noodles rice", "noodles noodles", "noodles vegetables", "noodles chicken", "vegetables chops", "vegetables ribs", "vegetables steak", "vegetables fish", "vegetables rice", "vegetables noodles", "vegetables vegetables", "vegetables chicken"]
	else:
		# the verbs should be for diy
		query_verbs = ["build", "make", "fix"]
		query_noun_phrases = ["a table", "a chair", "a shelf", "a bookshelf", "a desk", "a bed", "a broken bike", "a flat tire", "a wall", "a door", "a window", "a roof", "a house", "a car", "a computer", "a laptop", "a phone", "a smartphone", "a tablet", "a TV", "a television", "a radio", "a speaker", "a headphone", "a headset", "a microphone", "a camera", "a drone", "a robot", "a toy", "a game", "a puzzle", "a board game", "a card game", "a console", "a controller", "a keyboard", "a mouse", "a monitor", "a screen", "a display", "a projector", "a light", "a lamp", "a flashlight", "a torch", "a fan", "a heater", "a cooler", "a fridge", "a refrigerator", "a freezer", "a stove", "an oven", "a microwave", "a dishwasher", "a washing machine", "a dryer", "a vacuum cleaner", "a blender", "a mixer", "a juicer", "a toaster", "a coffee maker", "a kettle", "a pot", "a pan", "a knife", "a fork", "a spoon", "a plate", "a bowl", "a cup", "a glass", "a bottle", "a can", "a box", "a bag", "a backpack", "a suitcase", "a wallet", "a purse", "a hat", "a cap", "a shirt", "a t-shirt", "a jacket", "a coat", "a dress", "a skirt", "a pair of pants", "a pair of shorts", "a pair of shoes", "a pair of boots", "a pair of sandals", "a pair of slippers", "a pair of glasses", "a pair of sunglasses", "a pair of gloves", "a pair of socks", "a pair of underwear", "a pair of pajamas", "a pair of earrings", "a pair of bracelets", "a pair of rings", "a pair of necklaces", "a pair of watches", "a pair of belts", "a pair of scarves", "a pair of hats", "a pair of caps", "a pair of shirts", "a pair of t-shirts", "a pair of jackets", "a pair of coats", "a pair of dresses"]
	
	# part three of the query: filters like "as a beginner", "by myself", "quickly"
	query_filters = ["as a beginner", "by myself", "quickly", "easily", "at home", "", "", "", ""]
	
	# part four of the query: add words like "please"
	query_enders = [" please", ", please", ""]

	# generate the query
	query = random.choice(query_starters) + " " + random.choice(query_verbs) + " " + random.choice(query_noun_phrases) + " " + random.choice(query_filters) + random.choice(query_enders)

	return query

def test_vectordb(query):
    url = 'http://3.135.210.78:8001/vectordb'
    x = requests.post(url=url, json={"query_text": query, "top_N": 5, "security_key": "ZjCjUp#!QzsLaxhw_GJX@Cb?TmGc8%hDcvqyfDKA5$qRUr+ft?4qWB+Ve_vMJTh$u4h@96w2VS=P+?xTFdD8UC?f@8&3=W&e8DNK*Av$sV7#!@8gP+Pa75^waTm#nC6d"})

    print(x)

def test_questionclf(query):
    url = 'http://3.135.210.78:8001/question_clf'
    x = requests.post(url=url, json={"query_text": query, "security_key": "ZjCjUp#!QzsLaxhw_GJX@Cb?TmGc8%hDcvqyfDKA5$qRUr+ft?4qWB+Ve_vMJTh$u4h@96w2VS=P+?xTFdD8UC?f@8&3=W&e8DNK*Av$sV7#!@8gP+Pa75^waTm#nC6d"})

    print(x)

def test_rqclf(query):
    url = 'http://3.135.210.78:8001/request_query'
    x = requests.post(url=url, json={"query_text": query, "security_key": "zjcjup#!qzslaxhw_gjx@cb?tmgc8%hdcvqyfdka5$qrur+ft?4qwb+ve_vmjth$u4h@96w2vs=p+?xtfdd8uc?f@8&3=w&e8dnk*av$sv7#!@8gp+pa75^watm#nc6d"})

    print(x)

def pressure_test():
    quries = []
    for i in range(1000):
        quries.append(generateRandomQuery())
    
    start = time.time()

    for query in quries:
        test_rqclf(query)

    end = time.time()
    print("1000 queries")
    print(end - start)


if __name__ == '__main__':
    # test_sbert()
    # test_vectordb('Parkinson')
    test_questionclf('what\'s your name')
    test_questionclf('weed eater')
    print('finished testing')
    # pressure_test()
