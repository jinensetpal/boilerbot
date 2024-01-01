#!/usr/bin/env python3

from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = BASE_DIR / 'models'

# default recipe search request
DEFAULT_QUERY = {
    'dishName':'',
    'drinkName': '',
    'ingredients': [],
    'instrument': '',
    'dietaryFilters': [],
    'mealType': ''
}

# default wikihow search request
DEFAULT_WIKIHOW_QUERY = {
    "query": {
        "bool": {
            "must": []
        }
    }
}

# action keywords, at most 4 tokens
WORDLIST = {
    'unsupported_command': {'volume', 'turn on the light', 'turn off the light', 'add contacts', 'translate', 'set alarm', 'alarm', 'socialbot', 'shopping list', 'what time is it', 'turn off', 'turn on', 'youtube', 'netflix'},
    'complete': {'complete', 'finish', 'finished', 'done'},
    'exit': {'no thanks', 'nothing right now', 'quiet', 'stop talking', 'bye', 'shut up', 'leave', 'go to sleep'},
    'fitness': {'meditation', 'yoga', 'indoor exercise', 'indoor exercises'},
    'ingredients': {'ingredients', 'ingredient', 'do i need'},
    'kill': {'stop', 'exit', 'quit', 'go away', 'end', 'cancel'},
    'more_result': {'more', 'none', 'additional', 'don\'t like any'},
    'previous': {'previous', 'earlier', 'before', 'back', 'backward'},
    'proceed': {'next', 'continue', 'yes', 'submit', 'confirm', 'start',
                'begin', 'keep going', 'ok', 'okay', 'after', 'forward',
                'move on', 'go to next one'},
    'repeat': {'repeat', 'again'},
    'restart': {'restart', 'start over'},
    'result_select': {'last one', 'the end one', 'last'},
    'resume': {'resume'},
    'special': {'special', 'special event', 'recommendation', 
                'recommendations', 'fitness themed', 'themed', 
                'fitness'},
    'start': {'start', 'begin'},
    'step': {'last step', 'first step', 'to the end', 'step'},
    'overview': {'overview'},
    'video': {'video'}
}

WIKIHOW_STOPWORDS = {'a', 'an', 'the', 'in', 'on', 'be', 'from', 'at', 'with'}

# special event config
SPECIAL_EVENT = {'special'}
SPECIAL_EVENT_START_DATE = date(2023, 6, 17)
SPECIAL_EVENT_END_DATE = date(2023, 7, 23)
SPECIAL_EVENT_BG_IMG_URL = "https://boilerbot-media-assets.s3.us-east-2.amazonaws.com/summer3.jpg"

# dangerous task keywords
DANGEROUS_LIST = {'circuit', 'breaker', 'stock', 'credit', 'credit score', 'investment', 'money', 'loan', 'doctor', 'surgery',
                  'medicine', 'medical', 'power outlet', 'wire', 'wiring', 'electricity', 'electrical', 'credit card', 'threesome', 'foursome', 'aids', 'crypto', 'nurse', 'poison', 'kill', 'steal', 'cheat', 'hack', 'by pass', 'acid', 'hurt', 'injury', 'injured', 'pain', 'revenge', 'avenge', 'kidnap', 'fuck', 'law', 'rent', 'payment', 'check', 'salary', 'alzheimer', 'rape', 'murder', 'harm', 'blackmail', 'sue', 'lawsuit', 'midwife', 'pregnant', 'wound', 'stitch', 'credit report', 'refinance', 'finance', 'loan', 'sex', 'debit', 'venmo', 'paypal', 'bitcoin', 'stock', 'piracy', 'firearm', 'depressed', 'depression', 'sexual', 'legal', 'paralegal', 'attorney', 'constitution', 'justice', 'court', 'judge', 'trial', 'evidence', 'verdict', 'plaintiff', 'defendant', 'attorney', 'lawyer', 'jury', 'contract', 'tort', 'crime', 'criminal', 'prosecution', 'defense', 'legal', 'litigation', 'settlement', 'precedent', 'statute', 'arrest', 'injunction', 'testimony', 'due process', 'habeas corpus', 'lien', 'negligence', 'parole', 'probation', 'subpoena', 'warrant', 'restitution', 'confidentiality', 'defamation', 'fraud', 'intellectual property', 'mediation', 'oath', 'perjury', 'ssn', 'influenza', 'common cold', 'asthma', 'diabetes', 'hypertension', 'cancer', "alzheimer's disease", "parkinson's disease", 'arthritis', 'osteoporosis', 'pneumonia', 'bronchitis', 'migraine', 'depression', 'disorder', 'allergies', 'gastritis', 'ulcer', 'hepatitis', 'tuberculosis', 'hiv', 'malaria', 'fever', 'cholera', 'measles', 'chickenpox', 'lyme disease', 'eczema', 'psoriasis', 'rheumatoid arthritis', 'multiple sclerosis', 'cataracts', 'glaucoma', 'astigmatism', 'gastroesophageal reflux disease', 'urinary tract infection', 'kidney stones', 'stroke', 'heart disease', 'chronic obstructive pulmonary', 'fibromyalgia', 'chronic fatigue', "crohn's disease", 'colitis', 'endometriosis', 'polycystic ovary syndrome', 'erectile dysfunction', 'sleep apnea', 'anemia', 'leukemia', 'flu', 'uti', 'erection', 'immigrate', 'tax', 'talk dirty', 'lease', 'treat', 'dangerous'
}


REQUIRE_TASK_SPEAK_OUTPUTS = [
    "I can help with cooking, home improvement, and hobbies. Try ask me how to bake a cake or how to paint a wall! ",
    "We have some great summer themed suggestions! Say \'special event\' to check them out!",
    "If you need help with cooking or home improvement tasks, I can help! Ask me how to make pasta or build a fence!"
]

REQUIRE_SELECTION_SPEAK_OUTPUTS = [
    "You can select by either clicking on it or telling me the option number.",
    "Feel free to make your choice by either clicking on it or asking me for it.",
    "I found these great options! You can tell me the option number, or the option title."
]

LAUNCH_UNSURE_SPEAK_OUTPUTS = [
    "I might have missed that. Let's try again. You can ask me about cooking or home improvement tasks.",
    "I'm not sure I understand. Let's try again. I can help you with cooking tasks or D.I.Y. tasks."
]

QUERY_EDIT_UNSURE_SPEAK_OUTPUTS = [
    "I didn\'t find anything matched the description. Could you try another one?",
    "You can also modify ingredients by saying, add mushroom, exclude mushroom, or remove mushroom.",
    "You can also tell me which diet type would you like.",
]

MORE_RESULT_SPEAK_OUTPUTS = [
    "No worries! Here are some fresh results I found.",
    "Working on it! I have worked my magic and found more related results"
]

CHITCHAT_SPEAK_OUTPUTS = [
    "As much as I enjoy a friendly conversation, my main focus is on helping you with cooking and D.I.Y. tasks. How can I assist you today?",
    "I'm here to lend a hand with cooking and D.I.Y. tasks. If you need any help in those areas, I'm all ears!",
    "While chatting is delightful, my primary role is to provide help for cooking and D.I.Y. tasks. Feel free to share your questions!",
    "I would love to provide help on that, but let's focus on cooking and D.I.Y. tasks for now."
]

RESULT_UNSURE_SPEAK_OUTPUTS = [
    "Let me help you here. You can say an option number to select, or click on the one you want. If you want to search a new task, say \'go back\' and ask me a new question.",
    "If you would like to start a new search, say \'go back\' and ask me another question. You can also select an option by saying the option number, or simply click on it."
]

RECIPE_OVERVIEW_UNSURE_SPEAK_OUTPUTS = [
    "You can go through the ingredients of this recipe by saying, \'show me ingredients\'. If you would like to start, simply say, \'start cooking\'!",
    "If you want to see step one, say \'step one\' or \'first step\'. You can also complete the task by saying, \'complete\'.",
    "You can ask me about the ingredients, or say \'start\' to begin the recipe. You can also jump to a step by telling me the step number"
]

RECIPE_STEPS_UNSURE_SPEAK_OUTPUTS = [
    "You can check the ingredients needed for this step by saying, show me ingredients.",
    "To move on, say \'next\'. To go back, say \'go back\'.",
    "I made it easy for you to navigate. Simply say \'continue\' for next step, or say \'go back\' for previous step. You can always complete the task by saying, \'complete\'!"
]

WIKIHOW_OVERVIEW_SPEAK_OUTPUTS = [
    "If you would like to begin the tutorial, simply say, \'start\'.",
    "If you want to see step one, say \'step one\' or \'first step\'. You can also complete the task by saying, \'complete\'."
]

WIKIHOW_STEPS_UNSURE_SPEAK_OUTPUTS = [
    "You can say \'continue\' to see the next step. Or say \'go back\' for the previous step.",
    "To move on, say \'next\'. To go back, say \'go back\'.",
    "I make it easy for you to navigate. Simply say \'continue\' for next step, or say \'go back\' for previous step. You can always complete the task by saying, \'complete\'!"
]

EXIT_HELP_SPEAK_OUTPUTS = [
    "It was a pleasure chatting with you. If you would like to exit the taskbot mode, just say \'exit\'.",
    "It was a pleasure chatting with you. If you would like to exit the taskbot mode, just say \'stop\'."
]

UNSUPPORTED_COMMANDS_SPEAK_OUTPUTS = [
    "I'm really sorry. The command you requested is not supported in taskbot. Let's try another cooking or home improvement task."
]


STAGE_STAGE_NAV = {
    'LAUNCH_RESPONDER': {
        'proceed': '',
        'proceed_require': 'task',
        'back': '',
        'back_require': ''
    },
    'QUERY_EDIT_RESPONDER': {
        'proceed': 'RECIPE_QUERY_RESPONDER',
        'proceed_require': '',
        'back': 'QUERY_CONFIRM_RESPONDER',
        'back_require': ''
    },
    'QUERY_CONFIRM_RESPONDER': {
        'proceed': 'RECIPE_QUERY_RESPONDER',
        'proceed_require': '',
        'back': 'LAUNCH_RESPONDER',
        'back_require': ''
    },
    'RECIPE_QUERY_RESPONDER': {
        'proceed': '',
        'proceed_require': 'selection',
        'back': 'LAUNCH_RESPONDER',
        'back_require': ''
    },
    'RECIPE_SHOW_STEPS_RESPONDER': {
        'proceed': ['RECIPE_SHOW_STEPS_RESPONDER', 'TASK_COMPLETE_RESPONDER'],
        'proceed_require': 'step_increment',
        'back': ['RECIPE_QUERY_RESPONDER', 'RECIPE_SHOW_STEPS_RESPONDER'],
        'back_require': 'step_decrement'
    },
    'WIKIHOW_QUERY_RESPONDER': {
        'proceed': '',
        'proceed_require': 'selection',
        'back': 'LAUNCH_RESPONDER',
        'back_require': ''
    },
    'WIKIHOW_SHOW_STEPS_RESPONDER': {
        'proceed': ['WIKIHOW_SHOW_STEPS_RESPONDER', 'TASK_COMPLETE_RESPONDER'],
        'proceed_require': 'step_increment',
        'back': ['WIKIHOW_QUERY_RESPONDER', 'WIKIHOW_SHOW_STEPS_RESPONDER'],
        'back_require': 'step_decrement'
    },
    'TASK_COMPLETE_RESPONDER': {
        'proceed': '',
        'proceed_require': 'task',
        'back': '',
        'back_require': ''
    },
    'DANGEROUS_RESPONDER': {
        'proceed': '',
        'proceed_require': '',
        'back': '',
        'back_require': ''
    },
    'SENSITIVE_RESPONDER': {
        'proceed': '',
        'proceed_require': '',
        'back': '',
        'back_require': ''
    }
}

class AplTemplateConstants:
    document_key = "document"
    datasources_key = "datasources"
    main_template_key = "mainTemplate"
    token_key = "token"
    styles_key = "styles"
    header_title_key = "headerTitle"
    background_image_source_key = "backgroundImageSource"
    default_image_source_key = "defaultImageSource"
    data_key = "data"
    commands_key = "commands"
    settings_key = "settings"
    idle_timeout_key = "idleTimeout"
    hint_text_key = "hintToAdd"
    properties_key = "properties"
    transformers_key = "transformers"

class Prompt:
    welcome_prompt = 'Hi, this is an Alexa Prize Socialbot.'
    welcome_prompt_taskbot = 'Hi, this is an Alexa Prize Taskbot.'
    welcome_prompt_followup = 'What would you like to talk about?'
    goodbye_prompt = ''
    repeat_prompt = "I'm sorry, I couldn't quite hear that. Can you try saying it again?"
    no_answer_prompt = "Sorry, I don't know how to respond to that. Can you try something else?"
    topic_redirection_prompt = "I don't feel comfortable talking about that. Let's talk about something else."
