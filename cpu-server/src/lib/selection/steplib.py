#!/usr/bin/env python3
from copy import deepcopy
from datetime import date
import operator

from lib.const import *
from lib.remote_module.modules import get_number
from lib.utils import cleanup

from lib.parsing.parse_query import parse_action
from lib.parsing.parse_query_b import parse_action_b
from lib.parsing.parsing_utils import get_n_grams, get_fuzzy_similarity
from lib.selection.action.previous import back_action
from lib.selection.action.complete import complete_action
from lib.selection.action.end import end_action
from lib.selection.action.filter import filter_action
from lib.selection.action.proceed import proceed_action
from lib.selection.action.resume import resume_action
from lib.selection.action.restart import restart_action
from lib.selection.action.ingredients import read_ingredients_action
from lib.selection.action.result_select import result_select_action
from lib.selection.action.repeat import repeat_action
from lib.selection.action.step_n import step_n_action
from lib.selection.action.search_task import search_task_action
from lib.selection.action.unsure import unsure_action
from lib.utils import get_list_item_selected

wordlist = WORDLIST

def launch(state):
    text = getattr(state.current_state, 'text')
    tokens = get_n_grams(text)

    if wordlist['fitness'].intersection(tokens):
        domain_result = getattr(state.user_attributes, 'domain_clf')
        domain_result['domain'] == 'DIY'
        domain_result['score'] = 0.8
    elif wordlist['resume'].intersection(tokens):
        return resume_action(state)
    elif wordlist['complete'].intersection(tokens):
        return complete_action(state)
    elif wordlist['exit'].intersection(tokens):
        return end_action(state)
    
    domain_result = getattr(state.user_attributes, 'domain_clf')
    cleanup(state)
    return search_task_action(state)


def query_edit(state):
    intent = getattr(state.current_state, 'intent')
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    text = getattr(state.current_state, 'text')
    tokens = get_n_grams(text)

    if intent and intent == 'UserEvent':
        options = state.current_state.user_event.get('arguments')
        task_domain = getattr(state.user_attributes, 'task_domain')
        if options:
            if {'QUERY_EDIT_RESPONDER'}.intersection(set(options)):
                return 'QUERY_EDIT_RESPONDER'
            elif {'LAUNCH_RESPONDER'}.intersection(set(options)):
                cleanup(state)
                return 'LAUNCH_RESPONDER'
            elif {'RECIPE_QUERY_RESPONDER'}.intersection(set(options)):
                return 'RECIPE_QUERY_RESPONDER'
    elif curr_stage == 'QUERY_CONFIRM_RESPONDER' and {'no'}.intersection(tokens):
        return unsure_action(state)
    else:
        return parse_action_b(state)


def query_result(state):
    text = getattr(state.current_state, 'text')
    tokens = get_n_grams(text)
    task_domain = getattr(state.user_attributes, 'task_domain')
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    intent = getattr(state.current_state, 'intent')
    new_search_task = getattr(state.user_attributes, 'new_search')

    if getattr(state.user_attributes, 'new_search'):
        return search_task_action(state)
    
    if intent and intent == 'UserEvent':
        options = state.current_state.user_event.get('arguments')
        if options:
            if {'ListItemSelected'}.intersection(options):
                if task_domain == 'COOK':
                    if get_list_item_selected(state) > len(getattr(state.user_attributes, 'recipe_query_result')):
                        setattr(state.user_attributes, 'unsure', True)
                        return 'RECIPE_QUERY_RESPONDER'
                    setattr(state.user_attributes, 'current_step', -1)
                    return 'RECIPE_SHOW_STEPS_RESPONDER'
                else:
                    if get_list_item_selected(state) > len(getattr(state.user_attributes, 'wikihow_query_result')):
                        setattr(state.user_attributes, 'unsure', True)
                        return 'WIKIHOW_QUERY_RESPONDER'
                    setattr(state.user_attributes, 'current_step', -1)
                    return 'WIKIHOW_SHOW_STEPS_RESPONDER'
            elif {'INTENT.Restart'}.intersection(set(options)):
                return restart_action(state)
            elif {'RESET'}.intersection(set(options)) or any('INTENT.Filter' in option for option in options):
                return filter_action(state)
    
    if wordlist['more_result'].intersection(tokens):
        setattr(state.user_attributes, 'more_results', True)
        return curr_stage
    elif get_number(text) is not None or wordlist['result_select'].intersection(tokens):  # query result selection (voice)
        return result_select_action(state)
    else:
        # query result unsure
        return unsure_action(state)


def show_steps(state):
    text = getattr(state.current_state, 'text')
    tokens = get_n_grams(text)
    step = getattr(state.user_attributes, 'current_step', None)
    total_steps = getattr(state.user_attributes, 'n_steps', 1)
    directives = getattr(state.current_state, 'directive')
    intent = getattr(state.current_state, 'intent')
    curr_stage = getattr(state.user_attributes, 'curr_stage')

    if len(directives) > 1:
        # button behaviors (overview, steps)
        if directives[1] in ['INTENT.StartCooking', 'INTENT.StartWikihow', 'INTENT.NextStep']: return proceed_action(state)
        elif directives[1] == 'INTENT.PreviousStep': return back_action(state)
    elif directives == ['goBack']: return back_action(state)
    
    if wordlist['ingredients'].intersection(tokens): return step_n_action(state)
    elif wordlist['overview'].intersection(tokens): return back_action(state)
    elif wordlist['complete'].intersection(tokens): return complete_action(state)
    else: return unsure_action(state)


CUSTOM_STEP = {
    'LAUNCH_RESPONDER': launch,
    'TASK_COMPLETE_RESPONDER': launch,
    'DANGEROUS_RESPONDER': launch,
    'SENSITIVE_RESPONDER': launch,
    'RECIPE_QUERY_RESPONDER': query_result,
    'WIKIHOW_QUERY_RESPONDER': query_result,
    'RECIPE_SHOW_STEPS_RESPONDER': show_steps,
    'WIKIHOW_SHOW_STEPS_RESPONDER': show_steps,
    'QUERY_CONFIRM_RESPONDER': query_edit,
    'QUERY_EDIT_RESPONDER': query_edit,
}


def get_step(name):
    return CUSTOM_STEP.get(name, launch)
