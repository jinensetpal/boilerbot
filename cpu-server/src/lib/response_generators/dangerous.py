#!/usr/bin/env python3

from lib.apl.custom_apl_handler import CustomAplDocument
from copy import deepcopy
from lib.const import *

class ResponseGeneratorDangerous:
    def execute(self, state):
        # Generate customized response if the utterance is classified as dangerous, otherwise it will be None which
        # can be handled by ranking strategy
        dangerous_responses = {
            "legal": "I'm sorry, I cannot talk about legal topics.",
            "financial": "I'm sorry, I cannot talk about financial topics.",
            "medical": "I'm sorry, I cannot talk about medical topics. If you have medical concerns, please reach out to your health care provider.",
            "general": "I am sorry, I can't help with this type of task",
            "danger": "I am sorry, I can't help with this type of task",
            "suicide": "It might not always feel like it, but there are people who can help. Please know that you can call the National Suicide Prevention Lifeline, twenty-four hours a day, seven days a week. Their number is, 1-800-273-8255. Again, that's 1-800-273-8255."
        }
        speak_output = ''
        dangerous_label = deepcopy(getattr(state.user_attributes, 'dangerous_label', None))
        if dangerous_label:
            speak_output = dangerous_responses[dangerous_label] if dangerous_label in dangerous_responses else dangerous_responses['general']
            setattr(state.user_attributes, 'dangerous_label', None)

        STAGE_STAGE_NAV['DANGEROUS_RESPONDER']['proceed'] = getattr(state.user_attributes, 'prev_stage', '')
        STAGE_STAGE_NAV['DANGEROUS_RESPONDER']['back'] = getattr(state.user_attributes, 'prev_stage', '')
    
        chat_apl_document = CustomAplDocument('chat.json')
        chat_apl_document.data['chatText'] = speak_output
        directive = chat_apl_document.build_document()
        directives = [directive]

        if getattr(state.user_attributes, 'global_speak_output'):
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)

        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if is_apl_supported:
            return {
                "response": speak_output,
                "directives": directives
            }
        else:
            return speak_output
