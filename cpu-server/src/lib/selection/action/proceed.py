import random

from lib.const import *
from lib.parsing.parsing_utils import get_n_grams
from lib.selection.action.complete import complete_action
from lib.selection.action.step_n import step_n_action

wordlist = WORDLIST

def proceed_action(state):
    responder = None
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    curr_task_domain = getattr(state.user_attributes, 'task_domain')
    directives = getattr(state.current_state, 'directive')
    tokens = get_n_grams(getattr(state.current_state, 'text'))

    # Stage-Stage Forward Navigation
    next_stage = STAGE_STAGE_NAV[curr_stage]['proceed']
    requirement = STAGE_STAGE_NAV[curr_stage]['proceed_require']

    if not next_stage:
        if requirement == 'task':
            global_speak_output = random.choice(REQUIRE_TASK_SPEAK_OUTPUTS)
            setattr(state.user_attributes, 'global_speak_output', global_speak_output)
        elif requirement == 'selection':
            global_speak_output = random.choice(REQUIRE_SELECTION_SPEAK_OUTPUTS)
            setattr(state.user_attributes, 'global_speak_output', global_speak_output)
        responder = curr_stage

        if curr_stage in {'RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER'} and getattr(state.user_attributes, 'new_search'):
            global_speak_output = random.choice(LAUNCH_UNSURE_SPEAK_OUTPUTS)
            setattr(state.user_attributes, 'global_speak_output', global_speak_output)
            responder = 'LAUNCH_RESPONDER'
    else:
        responder = next_stage
    
    # Step Sensitive Stages Navigation
    if requirement == 'step_increment':
        intent = 'NextIntent'
        if len(directives) > 1 and directives[1] in {'INTENT.StartCooking', 'INTENT.StartWikihow'}:
            intent = 'StartIntent'
        elif wordlist['start'].intersection(tokens):
            intent = 'StartIntent'
        elif wordlist['step'].intersection(tokens):
            intent = 'StepIntent'

        step = getattr(state.user_attributes, 'current_step')
        total_steps = getattr(state.user_attributes, 'n_steps')
        started_cooking = getattr(state.user_attributes, 'started_cooking', False)
        started_wikihow = getattr(state.user_attributes, 'started_wikihow', False)

        if intent == 'StartIntent':
            if curr_stage == 'RECIPE_SHOW_STEPS_RESPONDER' and not started_cooking:
                setattr(state.user_attributes, 'started_cooking', True)
                step = 0
                responder = 'RECIPE_SHOW_STEPS_RESPONDER'
            elif curr_stage == 'WIKIHOW_SHOW_STEPS_RESPONDER' and not started_wikihow:
                setattr(state.user_attributes, 'started_wikihow', True)
                step = 0
                responder = 'WIKIHOW_SHOW_STEPS_RESPONDER'
        elif intent == 'StepIntent':
            responder = step_n_action(state)
            step = getattr(state.user_attributes, 'current_step')
        else:
            step += 1
            responder = 'RECIPE_SHOW_STEPS_RESPONDER' if curr_task_domain == 'COOK' else 'WIKIHOW_SHOW_STEPS_RESPONDER'

            if step == 0:
                if curr_stage == 'RECIPE_SHOW_STEPS_RESPONDER':
                    setattr(state.user_attributes, 'started_cooking', True)
                elif curr_stage == 'WIKIHOW_SHOW_STEPS_RESPONDER':
                    setattr(state.user_attributes, 'started_wikihow', True)
            if step == total_steps:
                responder = complete_action(state)

        setattr(state.user_attributes, 'current_step', step)

    return responder
