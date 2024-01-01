
def read_ingredients_action(state):
    responder = None
    curr_task_domain = getattr(state.user_attributes, 'task_domain')
    curr_stage = getattr(state.user_attributes, 'curr_stage')

    if curr_stage == 'RECIPE_SHOW_STEPS_RESPONDER':
        setattr(state.user_attributes, 'read_ingredients', True)
        responder = 'RECIPE_SHOW_STEPS_RESPONDER'

    return responder
