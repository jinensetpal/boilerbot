#!/usr/bin/env python3

from lib.apl.custom_apl_handler import CustomAplDocument
from lib.utils import cleanup
from copy import deepcopy
import random

DATASOURCE = {
        "mainText": '',
        "title": '',
        "recipeInfo": [],
        "imageSrc": ''
}

class ResponseGeneratorTaskComplete:
    def execute(self, state):
        document = CustomAplDocument('completion_v2.json')

        task_item = None
        if getattr(state.user_attributes, 'recipe'):
                task_item = getattr(state.user_attributes, 'recipe')
        elif getattr(state.user_attributes, 'wikihow'):
                task_item = getattr(state.user_attributes, 'wikihow')

        data = deepcopy(DATASOURCE)
        data['title'] = task_item.get('title')
        data['mainText'] = 'Bon Appetit!' if getattr(state.user_attributes, 'prev_task_domain') == 'COOK' else 'Job Done!'
        if getattr(state.user_attributes, 'prev_task_domain') == 'COOK':
                data['recipeInfo'] = [
                        f"{len(task_item.get('steps'))} Steps", 
                        f"{len(task_item.get('ingredients'))} Ingredients"]
        else:
                data['recipeInfo'] = [
                        f"{len(task_item.get('steps'))} Steps"
                ]
        data['imageSrc'] = task_item.get('thumbnail_url')
        document.data = data

        speak_output = "<amazon:emotion name='excited' intensity='medium'> Task complete! </amazon:emotion> To exit Taskbot mode, just say stop. Or ask anything to start a new search."

        if getattr(state.user_attributes, 'global_speak_output'):
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)

        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if is_apl_supported: return {"response": speak_output, "directives": [document.build_document()]}
        else: return {"response": speak_output}
