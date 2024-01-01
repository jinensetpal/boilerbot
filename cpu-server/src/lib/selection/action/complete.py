from lib.utils import cleanup

def complete_action(state):
    curr_task_domain = getattr(state.user_attributes, 'task_domain')
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    resume_task = getattr(state.user_attributes, 'resume_task')
    
    if curr_stage in ['RECIPE_SHOW_STEPS_RESPONDER', 'WIKIHOW_SHOW_STEPS_RESPONDER']:
        responder = 'TASK_COMPLETE_RESPONDER'
    if curr_stage not in ['RECIPE_SHOW_STEPS_RESPONDER', 'WIKIHOW_SHOW_STEPS_RESPONDER']:
        cleanup(state)
        responder = 'LAUNCH_RESPONDER'

    return responder
