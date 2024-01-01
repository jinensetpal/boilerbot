import random

from lib.const import *

def end_action(state):
    responder = getattr(state.user_attributes, 'curr_stage')
    global_speak_output = random.choice(EXIT_HELP_SPEAK_OUTPUTS)
    setattr(state.user_attributes, 'global_speak_output', global_speak_output)

    return responder
