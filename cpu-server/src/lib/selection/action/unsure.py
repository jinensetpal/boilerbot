import random

from lib.const import *

def unsure_action(state, search_task=False):
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    responder = curr_stage
    unsure_speak_output = None
    
    # B testing, add 'QUERY_CONFIRM_RESPONDER' and 'QUERY_EDIT_RESPONDER'
    if curr_stage in {'LAUNCH_RESPONDER', 'TASK_COMPLETE_RESPONDER', 'QUERY_CONFIRM_RESPONDER'}:
        unsure_speak_output = random.choice(LAUNCH_UNSURE_SPEAK_OUTPUTS)
        responder = 'LAUNCH_RESPONDER'
    elif curr_stage in {'QUERY_EDIT_RESPONDER'}:
        unsure_speak_output = random.choice(QUERY_EDIT_UNSURE_SPEAK_OUTPUTS)
    elif curr_stage in {'QUERY_CONFIRM_RESPONDER'}:
        unsure_speak_output = random.choice(QUERY_CONFIRM_UNSURE_SPEAK_OUTPUTS)
    elif curr_stage in {'RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER'}:
        unsure_speak_output = random.choice(RESULT_UNSURE_SPEAK_OUTPUTS)
    elif curr_stage == 'RECIPE_SHOW_STEPS_RESPONDER':
        step = getattr(state.user_attributes, 'current_step')
        unsure_speak_output = random.choice(RECIPE_STEPS_UNSURE_SPEAK_OUTPUTS)
        if step == -1:
            unsure_speak_output = random.choice(RECIPE_OVERVIEW_UNSURE_SPEAK_OUTPUTS)
    elif curr_stage == 'WIKIHOW_SHOW_STEPS_RESPONDER':
        step = getattr(state.user_attributes, 'current_step')
        unsure_speak_output = random.choice(WIKIHOW_STEPS_UNSURE_SPEAK_OUTPUTS)
        if step == -1:
            unsure_speak_output = random.choice(WIKIHOW_OVERVIEW_SPEAK_OUTPUTS)
    
    if search_task:
        unsure_speak_output = random.choice(LAUNCH_UNSURE_SPEAK_OUTPUTS)
        responder = 'LAUNCH_RESPONDER'

    setattr(state.user_attributes, 'global_speak_output', unsure_speak_output)
    return responder
