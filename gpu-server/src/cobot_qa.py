import time

RESPONSE_NOT_ALLOWED_SUBSTRINGS = {
    'Alexa,',
    'skill://',
    'Audio:',
    'please say that again',
    'please try that again',
    'catch that',
    'find the answer to the question I heard',
    'I didn\'t get that',
    'have an opinion on that',
    'skill',
    'skills',
    'you can',
    'try asking',
    "Here's something I found on",
    'Sorry, I don\'t know that'
}

def get_qa(query):
    start = time.time()

    evi_response = _call_evi_service(query)
    fc_response, rr_response = _call_qa_classification_service(query, evi_response)
    evi_response = process_response(evi_response)
    confidence = get_confidence(evi_response, fc_response, rr_response, query)
    print("QA Confidence: %s", confidence)

    end = time.time()
    print(f"Get QA Latency: {end - start}s")

    if confidence == 'confidence_high':
        return evi_response
    return "Sorry, I didn\'t find anything related. Please ask me another question, hopefully about cooking or d.i.y."

def create_qa_service_request(text, response):
    request = dict()
    request["turns"] = list()
    request["turns"].append([text, response])
    return request

def _call_evi_service(current_text):
    try:
        result = ''
        response = result['response']
    except Exception as ex:
        if current_text != '':
            print(f"An exception while calling QA service: {ex}")
        response = ""
    return response

def _call_qa_classification_service(text, response):
    fc = False
    rr = "0"
    request = create_qa_service_request(text, response)
    try:
        result = ''
        fc = result['qa_factoid_classifier_results']['results'][0]
        rr = result['qa_response_relevance_classifier_results']['results']['label']
        print('QA Factoid classifier returned => %s, QA Response Relevance Classifier => %s', fc, rr)
    except Exception as ex:
        print(f"An exception while calling qa classification service request: {ex}")
    return fc, rr

def get_confidence(evi_response, fc_response, rr_response, text):
    confidence = 'confidence_low'
    if evi_response and fc_response:
        confidence = 'confidence_high'
    elif evi_response and not fc_response and rr_response == "1":
        confidence = 'confidence_high'
    elif evi_response:
        confidence = 'confidence_medium'

    if confidence == 'confidence_high':
        confidence = 'confidence_medium'

    return confidence

def process_response(response):
    if response and any(string.lower() in response.lower() for string in RESPONSE_NOT_ALLOWED_SUBSTRINGS):
        return ""
    return response if response else ''
