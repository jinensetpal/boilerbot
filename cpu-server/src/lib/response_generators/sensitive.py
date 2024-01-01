#!/usr/bin/env python3

from lib.utils import generate_chat_response_display
from copy import deepcopy
from lib.const import *

class ResponseGeneratorSensitive:
    """
    Generate responses to sensitive utterance.
    """
    def execute(self, state):
        # Generate customized response if the utterance is classified as sensitive, otherwise it will be None which
        # can be handled by ranking strategy
        speak_output = ''
        sensitive_response = deepcopy(getattr(state.user_attributes, 'sensitive_response', None))
        if sensitive_response:
            speak_output = sensitive_response
            setattr(state.user_attributes, 'sensitive_response', None)

        STAGE_STAGE_NAV['SENSITIVE_RESPONDER']['proceed'] = getattr(state.user_attributes, 'prev_stage', '')
        STAGE_STAGE_NAV['SENSITIVE_RESPONDER']['back'] = getattr(state.user_attributes, 'prev_stage', '')

        if getattr(state.user_attributes, 'global_speak_output'):
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)

        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if sensitive_response == '':
            return None
        elif is_apl_supported:
            return { "response": speak_output, "directives": [generate_chat_response_display(speak_output)] }
        else:
            return speak_output
