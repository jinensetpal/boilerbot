from lib.const import *
from lib.parsing.parsing_utils import get_n_grams
from lib.selection.action.step_n import step_n_action

wordlist = WORDLIST

def back_action(state):
    responder = None
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    curr_task_domain = getattr(state.user_attributes, 'task_domain')
    directives = getattr(state.current_state, 'directive')
    tokens = get_n_grams(getattr(state.current_state, 'text'))

    # Stage-Stage Backward Navigation
    next_stage = STAGE_STAGE_NAV[curr_stage]['back']
    requirement = STAGE_STAGE_NAV[curr_stage]['back_require']

    if not next_stage:
        responder = curr_stage
    else:
        responder = next_stage
    
    # Step Sensitive Stages Navigation
    if requirement == 'step_decrement':
        step = getattr(state.user_attributes, 'current_step')
        total_steps = getattr(state.user_attributes, 'n_steps')

        intent = 'BackIntent'
        if len(directives) > 1 and directives[1] == 'INTENT.PreviousStep' and step == 0:
            intent = 'OverviewIntent'
        elif directives == ['goBack']:
            intent = 'ResultIntent'
        elif wordlist['overview'].intersection(tokens):
            intent = 'OverviewIntent'
        elif wordlist['step'].intersection(tokens):
            intent = 'StepIntent'

        if intent == 'ResultIntent':
            if curr_stage == 'RECIPE_SHOW_STEPS_RESPONDER':
                setattr(state.user_attributes, 'started_cooking', False)
                step = -2
                responder = 'RECIPE_QUERY_RESPONDER'
            elif curr_stage == 'WIKIHOW_SHOW_STEPS_RESPONDER':
                setattr(state.user_attributes, 'started_wikihow', False)
                step = -2
                responder = 'WIKIHOW_QUERY_RESPONDER'
        elif intent == 'OverviewIntent':
            step = -1
            if curr_stage == 'RECIPE_SHOW_STEPS_RESPONDER':
                setattr(state.user_attributes, 'started_cooking', False)
            elif curr_stage == 'WIKIHOW_SHOW_STEPS_RESPONDER':
                setattr(state.user_attributes, 'started_wikihow', False)
            responder = curr_stage
        elif intent == 'StepIntent':
            responder = step_n_action(state)
            step = getattr(state.user_attributes, 'current_step')
        else:
            step -= 1
            responder = 'RECIPE_SHOW_STEPS_RESPONDER' if curr_task_domain == 'COOK' else 'WIKIHOW_SHOW_STEPS_RESPONDER'

            if step == -1:
                if curr_stage == 'RECIPE_SHOW_STEPS_RESPONDER':
                    setattr(state.user_attributes, 'started_cooking', False)
                elif curr_stage == 'WIKIHOW_SHOW_STEPS_RESPONDER':
                    setattr(state.user_attributes, 'started_wikihow', False)
            if step < -1:
                if curr_task_domain == 'COOK':
                    responder = 'RECIPE_QUERY_RESPONDER'
                elif curr_task_domain == 'DIY':
                    responder = 'WIKIHOW_QUERY_RESPONDER'
        
        if step >= -1: setattr(state.user_attributes, 'current_step', step)
        else: setattr(state.user_attributes, 'current_step', None)
    
    return responder
