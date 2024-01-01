
def repeat_action(state):
    curr_stage = getattr(state.user_attributes, 'curr_stage')
    setattr(state.user_attributes, 'global_speak_output', getattr(state.user_attributes, 'last_legal_response'))

    return curr_stage
