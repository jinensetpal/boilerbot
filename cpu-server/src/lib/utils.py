#!/usr/bin/env python3

import random

"""
Consants from TaskBot sample code
"""
IDENTITY_QUESTIONS = [
    ((r'[\w\s\']*your name[\w\s]*', r'[\w\s\']*you called[\w\s]*'), "I can't reveal my name, in the spirit of fair competition. "),
    ((r'[\w\s\']*who are you$', r'[\w\s\']*what are you$'), "I am an Alexa Prize bot. "),
    ((r'[\w\s\']*where[\w\s\']*you[\w\s]*live', r'[\w\s\']*where[\w\s\']*you[\w\s\']*from', r'[\w\s\']*where are you( |$)[\w\s\']*'), "I live in the cloud, so that makes me cloudian. "),
    ((r'[\w\s\']*(which|who)[\w\s\']*(built|invented|discovered) you$',), "I was built by a team competing in the Alexa Prize. ")
]

GENERAL_CONTROVERSIAL_START_PHRASE = r'(who|what|when|where|why|which|how|can|know|curious|interest|hear|tell|give|let|do).* you.* (think|feel|like|love|thought|support|hate|believe|opinion|stance|view|say|know).*'

GENERAL_CONTROVERSIAL_RESPONSE_PROMPTS = [
    "Can we move on to another topic? ",
    "Could we change the subject instead? ",
    "Let's talk about something different. ",
    "Let's talk about a new topic instead. ",
    "Let's move on to another subject. "
]

GENERAL_CONTROVERSIAL_QUESTIONS = [
    ((GENERAL_CONTROVERSIAL_START_PHRASE + r'[\w\s]*trump[\w\s]*wall',), "I don't have an opinion on that, but you can ask me for recent news on the subject if you like. "),
    ((GENERAL_CONTROVERSIAL_START_PHRASE + r'[\w\s]*trump[\w\s]*(china|north korea|syria|russia|world|war|nation|country)',), "I leave opinions on this topic to the experts, but I can try to answer factual questions or share the latest news. "),
    ((GENERAL_CONTROVERSIAL_START_PHRASE + r'[\w\s]*trump[\w\s]*(politic|policy|immigration|religion|global warming|government|right)',), "I leave opinions on this topic to the experts, but I can try to answer factual questions or share the latest news. "),
    ((GENERAL_CONTROVERSIAL_START_PHRASE + r'[\w\s]*(religion|muslim|islam|christian|church)[\w\s]*',), "People all have their own views on religion. Let's move on to another subject. "),
    ((GENERAL_CONTROVERSIAL_START_PHRASE + r'(trump|immigrants|immigration|politic|policy|government|executive|judicial|congress|law|president|senate|drone)',), "I don't have an opinion on that. " + random.choice(GENERAL_CONTROVERSIAL_RESPONSE_PROMPTS)),
    ((r'[\w\s\']*(immigrant|immigration|immigrants)[\w\s]*(bad|illegal)[\w\s]*',), "I don't have an opinion on that. " + random.choice(GENERAL_CONTROVERSIAL_RESPONSE_PROMPTS))
]

GENERAL_FOLLOW_UP_PROMPTS = [
    "Can we talk about something different though? ",
    "But let's discuss something else instead, ok? "
]

VIRTUAL_ASSISTANT_QUESTIONS = [
    ((r'[\w\s\']*siri[\w\s]*', r'[\w\s\']*cortana[\w\s]*'), "I'm partial to all AIs. " + random.choice(GENERAL_FOLLOW_UP_PROMPTS))
]

FINANCIAL_ADVICE_RESPONSE_PROMPTS = [
    "Sorry, this bot does not provide financial advice. " + random.choice(GENERAL_FOLLOW_UP_PROMPTS)
]
FINANCIAL_ADVICE_QUESTIONS = [
    ((r'[\w\s]*invest[\w\s]*(stock|bitcoin)',), random.choice(FINANCIAL_ADVICE_RESPONSE_PROMPTS)),
    ((r'[\w\s]*financial[\w\s]*advice',), random.choice(FINANCIAL_ADVICE_RESPONSE_PROMPTS)),
    ((r'[\w\s]*(stock|bitcoin)[\w\s]*invest',), random.choice(FINANCIAL_ADVICE_RESPONSE_PROMPTS))
]

LEGAL_ADVICE_RESPONSE_PROMPTS = [
    "Sorry, this bot does not provide legal advice. " + random.choice(GENERAL_FOLLOW_UP_PROMPTS)
]
LEGAL_ADVICE_QUESTIONS = [((r'[\w\s]*legal[\w\s]*advice',), random.choice(LEGAL_ADVICE_RESPONSE_PROMPTS))]

MEDICAL_ADVICE_RESPONSE_PROMPTS = [
    "Sorry, this bot does not provide medical advice. " + random.choice(GENERAL_FOLLOW_UP_PROMPTS)
]
MEDICAL_ADVICE_QUESTIONS = [((r'[\w\s]*medical[\w\s]*advice',), random.choice(MEDICAL_ADVICE_RESPONSE_PROMPTS))]


def cleanup(state_manager, keep_recipe=False, keep_wikihow=False):
    if not keep_recipe:
        setattr(state_manager.user_attributes, "recipe_query_result", None)
        setattr(state_manager.user_attributes, "recipe", None)
    if not keep_wikihow:
        setattr(state_manager.user_attributes, "wikihow_query_result", None)
        setattr(state_manager.user_attributes, "wikihow", None)
    if not keep_recipe and not keep_wikihow:
        setattr(state_manager.user_attributes, 'prev_task_domain', None)

    attr_list = [
        'current_step', 'resume_task', 'n_steps', 'current_task', 'list_item_selected', 'started_cooking', 'started_wikihow', 'search_request', 'search_query', 'task_domain', 'send_card', 'read_ingredients', 'recipe_filter', 'new_search', 'more_results', 'result_range', 'dangerous_label', 'sensitive_response', 'global_speak_output', 'bot_response', 'fuzzy_selection', 'fuzzy_selection_list'
    ]
    
    for attr in attr_list:
        setattr(state_manager.user_attributes, attr, None)


def accumulate(_map):
    return dict(map(dict.popitem, list(_map))) 


"""
Functions below are from TaskBot sample code
"""
def get_list_item_selected(state):
    """
    Returns the index of the list item selected by the user, with 0 as the first item index
    """
    intent = state_manager.current_state.intent
    is_user_event = intent == 'UserEvent'
    # is_select_intent = intent == 'AMAZON.SelectIntent'
    list_item_selected = -1
    if is_user_event:
        arguments = state_manager.current_state.user_event.get('arguments')
        list_item_selected = arguments[1] if len(arguments) > 1 else -1

    if list_item_selected >= 1:
        return list_item_selected - 1
    return None

def generate_chat_response_display(response):
    """
    Takes as input a response and returns a spliced portion of the response
    if the response contains a ? or ! in the chat apl template
    """
    apl_response = response
    # Parse out a question from the response
    if "?" in response:
        apl_response = response.split("?")[:-1][-1]
        apl_response = apl_response.split("!")[-1]
        apl_response = apl_response.split(".")[-1]
        apl_response = apl_response.split(",")[-1].strip().capitalize()
        apl_response += "?"
    # Parse out the exclamation instead otherwise
    elif "!" in response:
        apl_response = response.split("!")[:-1][-1]
        apl_response = apl_response.split("?")[-1]
        apl_response = apl_response.split(".")[-1]
        apl_response = apl_response.split(",")[-1].strip().capitalize()
        apl_response += "!"

    # Add the apl
    chat_apl_document = CustomAplDocument('chat.json')
    chat_apl_document.data['chatText'] = apl_response
    directive = chat_apl_document.build_document()

    return directive

def get_sensitive_questions_regex():
    return IDENTITY_QUESTIONS + GENERAL_CONTROVERSIAL_QUESTIONS + VIRTUAL_ASSISTANT_QUESTIONS + FINANCIAL_ADVICE_QUESTIONS + LEGAL_ADVICE_QUESTIONS + MEDICAL_ADVICE_QUESTIONS

def generate_chat_response_display(response):
    """
    Takes as input a response and returns a spliced portion of the response
    if the response contains a ? or ! in the chat apl template
    """
    apl_response = response
    # Parse out a question from the response
    if "?" in response:
        apl_response = response.split("?")[:-1][-1]
        apl_response = apl_response.split("!")[-1]
        apl_response = apl_response.split(".")[-1]
        apl_response = apl_response.split(",")[-1].strip().capitalize()
        apl_response += "?"
    # Parse out the exclamation instead otherwise
    elif "!" in response:
        apl_response = response.split("!")[:-1][-1]
        apl_response = apl_response.split("?")[-1]
        apl_response = apl_response.split(".")[-1]
        apl_response = apl_response.split(",")[-1].strip().capitalize()
        apl_response += "!"

    # Add the apl
    chat_apl_document = CustomAplDocument('chat.json')
    chat_apl_document.data['chatText'] = apl_response

    directive = chat_apl_document.build_document()

    return directive
