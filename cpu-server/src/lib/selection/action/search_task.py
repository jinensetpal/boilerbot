import random
from copy import deepcopy

from lib.const import *
from lib.utils import cleanup
from lib.remote_module.modules import get_qa
from lib.parsing.parse_query import parse_action
from lib.parsing.parse_query_b import parse_action_b
from lib.selection.action.complete import complete_action
from lib.selection.action.step_n import step_n_action
from lib.selection.action.result_select import result_select_action
from lib.selection.action.previous import back_action
from lib.selection.action.proceed import proceed_action
from lib.selection.action.unsure import unsure_action

def search_task_action(state, override=None):
    domain_result = deepcopy(getattr(state.user_attributes, 'domain_clf'))
    text = getattr(state.current_state, 'text')
    bot_response = getattr(state.user_attributes, 'bot_response', '')
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    responder = None

    if domain_result['domain'] == 'COOK':
        setattr(state.user_attributes, 'task_domain', domain_result['domain'])
        setattr(state.user_attributes, 'prev_task_domain', domain_result['domain'])
        setattr(state.user_attributes, 'search_query', text)
        new_search_cleanup(state)
        
        # B testing
        if state.current_state.is_experiment == True:
            responder = parse_action_b(state)
        else:
            responder = parse_action(state)
    elif domain_result['domain'] == 'DIY':
        setattr(state.user_attributes, 'task_domain', domain_result['domain'])
        setattr(state.user_attributes, 'prev_task_domain', domain_result['domain'])
        setattr(state.user_attributes, 'search_query', text)
        new_search_cleanup(state)
        responder = 'WIKIHOW_QUERY_RESPONDER'
    elif domain_result['domain'] == 'CHITCHAT':
        responder = getattr(state.user_attributes, 'curr_stage')
        if responder == 'TASK_COMPLETE_RESPONDER':
            responder = 'LAUNCH_RESPONDER'
        setattr(state.user_attributes, 'global_speak_output', random.choice(CHITCHAT_SPEAK_OUTPUTS))
    elif domain_result['domain'] == 'QUESTION':
        responder = getattr(state.user_attributes, 'curr_stage')
        if responder == 'TASK_COMPLETE_RESPONDER':
            responder = 'LAUNCH_RESPONDER'
        qa_response = get_qa(text)
        if qa_response:
            setattr(state.user_attributes, 'global_speak_output', qa_response)
    elif domain_result['domain'] == 'UNSUPPORTED_COMMAND':
        responder = getattr(state.user_attributes, 'curr_stage')
        if responder == 'TASK_COMPLETE_RESPONDER':
            responder = 'LAUNCH_RESPONDER'
        setattr(state.user_attributes, 'global_speak_output', random.choice(UNSUPPORTED_COMMANDS_SPEAK_OUTPUTS))
    else:
        cleanup(state)
        responder = unsure_action(state, search_task=True)

    return responder


def new_search_cleanup(state):
    attr_list = [
        'wikihow_query_result', 'wikihow', 'recipe_query_result', 'recipe', 'current_step', 'n_steps', 'resume_task', 'current_task', 'list_item_selected', 'started_cooking', 'started_wikihow', 'search_request', 'send_card', 'read_ingredients', 'recipe_filter', 'new_search', 'special_event', 'more_results', 'result_range', 'dangerous_label', 'sensitive_response', 'global_speak_output', 'bot_response', 'fuzzy_selection', 'fuzzy_selection_list'
    ]

    for attr in attr_list:
        setattr(state.user_attributes, attr, None)
