from lib.utils import cleanup

def resume_action(state):
    responder = None
    prev_task_domain = getattr(state.user_attributes, 'prev_task_domain')
    setattr(state.user_attributes, 'task_domain', prev_task_domain)
    task_item = getattr(state.user_attributes, 'recipe') if prev_task_domain == 'COOK' else getattr(state.user_attributes, 'wikihow')

    if task_item:
        if prev_task_domain == 'COOK':
            responder = 'RECIPE_SHOW_STEPS_RESPONDER'
        elif prev_task_domain == 'DIY':
            responder = 'WIKIHOW_SHOW_STEPS_RESPONDER'
        # setattr(state.user_attributes, 'current_step', -1)
        if getattr(state.user_attributes, 'current_step', False) is None:
            setattr(state.user_attributes, 'current_step', -1)
        setattr(state.user_attributes, 'resume_task', True)
    else:
        responder = 'LAUNCH_RESPONDER'
        cleanup(state)
        setattr(state.user_attributes, 'unsure', True)
    
    return responder
