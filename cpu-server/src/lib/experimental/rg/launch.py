import random
from datetime import date
from copy import deepcopy
from lib.apl.custom_apl_handler import CustomAplDocument
from lib.const import *

# change 'backgroundImage' for special event
DATASOURCE = {
    "launch_data": {
        "centerText": "Ask me anything about<br>cooking or DIY : )",
        "suggested": [
            "How to cook chicken",
            "Steak recipe with garlic and onion",
            "How to change iPhone wallpaper?",
            "I want to cook some fish",
            "Fix my bike!",
            "How to pet my cat?"
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

        prev_task_domain = getattr(state.user_attributes, 'prev_task_domain', None)
        if prev_task_domain == 'COOK': task_item = getattr(state.user_attributes, 'recipe')
        else: task_item = getattr(state.user_attributes, 'wikihow')

        if task_item: speak_output = f"Last time we were working on {task_item.get('title')}. If you want to keep working on it, just say resume. If you have already completed this task, just say complete."
        else: speak_output = "Try asking me how to do a task like build a fence or search for a recipe like baked potato."
        
        # check if to show special event
        CURRENT_DATE = date.today()
        if SPECIAL_EVENT_START_DATE <= CURRENT_DATE <= SPECIAL_EVENT_END_DATE:
            speak_output = f"<amazon:emotion name='excited' intensity='medium'> We are officially in summer! </amazon:emotion> I can help with cooking, home improvement and summer activities. You can ask me about our special event to check it out, or ask me how to swim or even how to make a smoothie! What would you like to do?"

        unsure_status = deepcopy(getattr(state.user_attributes, 'unsure'))
        if unsure_status:
            cleanup(state)
            speak_output = f"Sorry, I'm not sure about that. {speak_output}"

        dangerous_status = deepcopy(getattr(state.user_attributes, 'dangerous'))
        if dangerous_status:
            speak_output = "I'm sorry, I can\'t help with this type of task. Is there another task I can help you with?"
            setattr(state.user_attributes, 'dangerous', None)

        document.data = data

        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if not is_apl_supported: return {'response': speak_output}
        else: return {'response': speak_output, 'directives': [document.build_document()]}
