from lib.remote_module.modules import get_number
from lib.parsing.parsing_utils import get_n_grams
from lib.selection.action.complete import complete_action
from lib.selection.action.unsure import unsure_action

def step_n_action(state):
    responder = None
    curr_task_domain = getattr(state.user_attributes, 'task_domain')
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    step = getattr(state.user_attributes, 'current_step')
    total_steps = getattr(state.user_attributes, 'n_steps')
    text = getattr(state.current_state, 'text').lower()
    tokens = get_n_grams(text)
    unsure_status = False

    if curr_stage in ['RECIPE_SHOW_STEPS_RESPONDER', 'WIKIHOW_SHOW_STEPS_RESPONDER']:
        if {'final', 'last'}.intersection(tokens):
            step = total_steps - 1
        elif {'beginning'}.intersection(tokens):
            step = 0
        elif {'previous'}.intersection(tokens):
            step -= 1
        elif {'next step'}.intersection(tokens):
            step += 1
        else:
            number = get_number(text)
            if number is None:
                unsure_status = True
            elif number < 0 or number > total_steps:
                unsure_status = True
            else:
                step = number - 1

    setattr(state.user_attributes, 'current_step', step)
    
    # enter step n from overview
    if curr_stage == 'RECIPE_SHOW_STEPS_RESPONDER' and not getattr(state.user_attributes, 'started_cooking', False) and not unsure_status:
        setattr(state.user_attributes, 'started_cooking', True)
        responder = 'RECIPE_SHOW_STEPS_RESPONDER'
    elif curr_stage == 'WIKIHOW_SHOW_STEPS_RESPONDER' and not getattr(state.user_attributes, 'started_wikihow', False) and not unsure_status:
        setattr(state.user_attributes, 'started_wikihow', True)
        responder = 'WIKIHOW_SHOW_STEPS_RESPONDER'
    else:   # enter step n from steps
        responder = 'RECIPE_SHOW_STEPS_RESPONDER' if curr_task_domain == 'COOK' else 'WIKIHOW_SHOW_STEPS_RESPONDER'
    
    if step == total_steps:
            responder = complete_action(state)
    
    if unsure_status:
        responder = unsure_action(state)

    return responder
