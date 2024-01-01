#!/usr/bin/env python3


from lib.apl.custom_apl_handler import CustomAplDocument
from lib.utils import cleanup
from copy import deepcopy
from datetime import date
from lib.const import *
import random

DATASOURCE = {
    "launch_data": {
        "centerText": "Ask me anything about<br>cooking or DIY tasks: )",
        "suggested": [
            "How to make smoothie?",
            "Salad recipes.",
            "How to eat a balanced meal?",
            "How to do a meditation?",
            "How to do yoga?",
            "How to do indoor exercises?"
        ],
        "backgroundImage": "https://boilerbot-media-assets.s3.us-east-2.amazonaws.com/bg2.jpg"
    }
}

class ResponseGeneratorLaunch:
    """
    If the user has an ongoing task, ask if they want to continue or complete it.
    Otherwise, share suggestions for what the user should try.
    """
    def execute(self, state):
        document = CustomAplDocument('launch_v2.json')
        data = deepcopy(DATASOURCE.get('launch_data'))
        # document = CustomAplDocument('launch_v3.json')
        # data = deepcopy(DATASOURCE.get('launch_data'))

        prev_task_domain = getattr(state.user_attributes, 'prev_task_domain', None)
        if prev_task_domain == 'COOK': task_item = getattr(state.user_attributes, 'recipe')
        else: task_item = getattr(state.user_attributes, 'wikihow')
        
        speak_output = "You can ask me how to do a D.I.Y. task like making a lego car, or search for a recipe like mashed potato."
        
        # check if to show special event
        CURRENT_DATE = date.today()
        if SPECIAL_EVENT_START_DATE <= CURRENT_DATE <= SPECIAL_EVENT_END_DATE:
            speak_output = "I can help with cooking, home improvement and achieve your fitness goals. Say \'special event\' to see our fitness themed suggestions, or ask me how to make a salad or how to do a meditation. What would you like?"

        # resume speak output
        if task_item:
            speak_output = f"Last time we were working on {task_item.get('title')}. If you want to keep working on it, just say \'resume\'. If you have completed this task, just say \'complete\'."

        # B testing
        if state.current_state.is_experiment == True:
            speak_output = "I'm here to help with cooking or home improvement tasks. You can ask me about recipe like mashed potato, or D.I.Y. tutorial like how to paint wall. What would you like to do?"

        # override default speakoutput
        if getattr(state.user_attributes, 'global_speak_output'):
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)

        document.data = data
        setattr(state.user_attributes, 'last_legal_response', speak_output)

        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if not is_apl_supported: return {'response': speak_output}
        else: return {'response': speak_output, 'directives': [document.build_document()]}
