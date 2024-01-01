#!/usr/bin/env python3

from copy import deepcopy
import random
import json

from lib.apl.custom_apl_handler import CustomAplDocument
from lib.utils import get_list_item_selected

DATASOURCE = {
    "steps": {
        "title": "",
        "returnButtonText": "See other tutorials",
        "mainParagraph": "",
        "currentPage": 0,
        "totalPages": 0,
        "imageSrc": "",
        "echoDotHintText": "Alexa, next step.",
        "currentProg": 499,
        "totalProg": 500,
        "button1Text": "Previous",
        "button2Text": "Next",
        "hasParts": False,
        "partNames": []
    },
    'overview': {
        "title": "",
        "steps": [],
        "methodsImages": [],
        "hasVideo": False
    }
}

class ResponseGeneratorWikihowShowSteps:
    """
    Get the steps for the current task and display them as a text list
    and get the ingredients for cooking tasks and display them in a detail page
    """

    def execute(self, state):
        resume_task = getattr(state.user_attributes, 'resume_task', False)
        wikihow_query_result = getattr(state.user_attributes, 'wikihow_query_result', None)
        current_step = getattr(state.user_attributes, 'current_step', None)
        started_wikihow = getattr(state.user_attributes, 'started_wikihow', False)

        if not resume_task:
            current_task = getattr(state.user_attributes, 'current_task', None)
            list_item_selected = getattr(state.user_attributes, 'list_item_selected', None)
            if current_task is not None: list_item_selected = getattr(state.user_attributes, 'list_item_selected')
            if list_item_selected is None: list_item_selected = get_list_item_selected(state)

            setattr(state.user_attributes, 'list_item_selected', list_item_selected)

            wikihow_item = wikihow_query_result[list_item_selected]
        else:
            wikihow_item = getattr(state.user_attributes, 'wikihow', None)

        if started_wikihow:
            if current_step == 0:
                if not resume_task:
                    current_step, speak_output, document = self._get_wikihow_steps(wikihow_item, card=True)
                else:
                    current_step, speak_output, document = self._get_wikihow_steps(wikihow_item)
            else:
                current_step, speak_output, document = self._get_wikihow_steps(wikihow_item)
        else:
            speak_output, document = self._get_wikihow_overview(wikihow_item, current_step)

        setattr(state.user_attributes, 'current_step', current_step)
        setattr(state.user_attributes, 'started_wikihow', started_wikihow)

        if getattr(state.user_attributes, 'global_speak_output'):
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)


        setattr(state.user_attributes, 'last_legal_response', speak_output)
        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if not is_apl_supported: return {'response': speak_output}
        else: return {'response': speak_output, 'directives': [document]}

    # Add HTML to steps/partNames
    def add_span(self, val):
        return f"<span color='rgba(255,255,255,0.4)'>{val}</span>"

    # Wikihow Overview
    def _get_wikihow_overview(self, selected_item, current_step):
        """
        Returns response, detail APL document with text and image, and scroll command
        """
        wikihow_item = selected_item
        wikihow_title = wikihow_item.get('title')
        n_steps = len(wikihow_item.get('steps'))

        document = CustomAplDocument('wikihow_preview_v2.json')
        data = deepcopy(DATASOURCE.get('overview'))

        data['title'] = wikihow_title
        steps_placeholder = "<br><span color='rgba(0,0,0,0)'>====<br> ====<br ====<br> ====<br>====<br> ====<br> ==== ==== ====<br>===== ==== ===== ===== ===== ===== =====</span>"
        data['steps'] = [step.get('text') for step in wikihow_item.get('steps')]
        data['steps'][-1] += steps_placeholder
        images_placeholder = [' ', ' ', ' ']
        data['methodsImages'] = list(set([step.get('image') for step in wikihow_item.get('steps')])) + images_placeholder
        data['hasVideo'] = False

        speak_output = "Great! Before we get started, please be careful when using any tools or equipment. " \
                        f"Remember, safety first! OK, {wikihow_title} has {n_steps} steps. " \
                        "Once you are ready, just say, start."
        
        unsure_status = deepcopy(getattr(state.user_attributes, 'unsure'))
        if unsure_status:
            setattr(state.user_attributes, 'unsure', False)
            is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
            speak_output = "Sorry, I'm unsure about it. Could you try something else?"

        document.data = data

        setattr(state.user_attributes, 'wikihow', wikihow_item)
        setattr(state.user_attributes, 'n_steps', n_steps)
        # setattr(state.user_attributes, 'current_task', wikihow_title)
        setattr(state.user_attributes, 'current_task', getattr(state.user_attributes, 'search_query'))
        setattr(state.user_attributes, 'prev_task_domain', getattr(state.user_attributes, 'task_domain'))
        return speak_output, document.build_document()

    # Wikihow Steps
    def _get_wikihow_steps(self, selected_item, card=False):
        if card: setattr(state.user_attributes, 'send_card', True)
        else: setattr(state.user_attributes, 'send_card', None)

        wikihow_item = selected_item
        current_step = state.user_attributes.current_step
        n_steps = len(wikihow_item.get('steps'))
        setattr(state.user_attributes, 'wikihow', wikihow_item)

        step = wikihow_item.get('steps')[current_step]
        step_detail = step.get('text').replace("approx.", "approximately").rstrip('. ') + '.'

        document = CustomAplDocument('wikihow_steps_v2.json')
        data = deepcopy(DATASOURCE.get('steps'))

        data['title'] = wikihow_item.get('title')
        data['mainParagraph'] = step_detail + '<br>'
        data['currentPage'] = current_step + 1
        data['totalPages'] = n_steps
        # show full progress bar
        if data.get('currentPage') == data.get('totalPages'):
            data['currentProg'] = 999
            data['totalProg'] = 1000
        else:
            data['currentProg'] = data.get('currentPage')
            data['totalProg'] = data.get('totalPages')
        
        data['imageSrc'] = wikihow_item.get('thumbnail_url')
        data['button1Text'] = 'Overview' if current_step == 0 else 'Previous'
        data['button2Text'] = 'Complete' if current_step == n_steps - 1 else 'Next'
        data['hasParts'] = True if wikihow_item.get('has_parts') else False

        if wikihow_item.get('has_parts'):
            print('Wikihow Item Has Parts')
            current_part = wikihow_item.get('steps')[current_step].get('part')
            for i in range(len(wikihow_item.get('part_names'))):
                if current_part == wikihow_item.get('part_names')[i]:
                    data['partNames'].append(f"{str(i + 1)}. {current_part}")
                else:
                    data['partNames'].append(self.add_span(f"{str(i + 1)}. {wikihow_item.get('part_names')[i]}"))

        step_num = current_step + 1
        if step_num == 1:
            speak_output = f"Here is step one. To continue, just say next. {step_detail}"
        elif step_num == 2:
            speak_output = f"Here is step two. To go back, just say previous. {step_detail}"
        else:
            speak_output = f"Step {str(step_num)}. {step_detail}"

        if getattr(state.user_attributes, 'unsure'):
            setattr(state.user_attributes, 'unsure', False)
            is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
            speak_output = "Sorry, I'm unsure about it. Could you try something else?"

        document.data = data

        return current_step, speak_output, document.build_document()
