import operator

from lib.remote_module.modules import get_number
from lib.parsing.parsing_utils import get_n_grams
from lib.selection.action.unsure import unsure_action

def result_select_action(state):
    responder = None
    curr_task_domain = getattr(state.user_attributes, 'task_domain')
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    text = getattr(state.current_state, 'text').lower()
    tokens = get_n_grams(text)
    list_item_selected = None
    result_range = getattr(state.user_attributes, 'result_range')
    if not result_range: result_range = [0, 5]
    range_min, range_max = result_range[0], result_range[1]
    n_candidates = range_max

    is_apl_supported = state.current_state.supported_interfaces.get('apl', False)

    if curr_stage in ['RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER']:
        if {'final', 'last'}.intersection(tokens):
            if is_apl_supported: list_item_selected = range_max - 1
            else: list_item_selected = range_max - 1
        elif {'beginning'}.intersection(tokens):
            list_item_selected = range_min
        elif get_number(text):
            number = get_number(text)
            if not number: list_item_selected = None
            else: list_item_selected = number + range_min - 1
        
        if list_item_selected < 0 or list_item_selected >= range_max: list_item_selected = None

    setattr(state.user_attributes, 'list_item_selected', list_item_selected)

    if curr_stage == 'RECIPE_QUERY_RESPONDER' and list_item_selected is not None: responder = 'RECIPE_SHOW_STEPS_RESPONDER'
    elif curr_stage == 'WIKIHOW_QUERY_RESPONDER' and list_item_selected is not None: responder = 'WIKIHOW_SHOW_STEPS_RESPONDER'

    if list_item_selected is None:
        responder = unsure_action(state)
    else:
        setattr(state.user_attributes, 'current_step', -1)


    return responder
