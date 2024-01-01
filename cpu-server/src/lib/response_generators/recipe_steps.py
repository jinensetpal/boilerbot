#!/usr/bin/env python3

from copy import deepcopy
import random
import json

from lib.parsing.parsing_utils import get_step_ingredients
from lib.apl.custom_apl_handler import CustomAplDocument
from lib.utils import get_list_item_selected

DATASOURCE = {
    "steps": {
        "title": "",
        "mainParagraph": "",
        "ingredients": [],
        "currentPage": 0,
        "totalPages": 0,
        "imageSrc": "",
        "echoDotHintText": "Alexa, next step.",
        "currentProg": 499,
        "totalProg": 500,
        "button1Text": "Previous",
        "button2Text": "Next"
    },
    "overview": {
        "title": "",
        "steps": [],
        "ingredientsAndTools": [
            "<strong>Ingredients</strong>",
        ]
    }
}

class ResponseGeneratorRecipeShowSteps:
    """
    Get the steps for the current task and display them as a text list
    and get the ingredients for cooking tasks and display them in a detail page
    """

    def execute(self, state):
        # Retrieve current task from state manager
        resume_task = getattr(state.user_attributes, 'resume_task', False)
        recipe_query_result = getattr(state.user_attributes, 'recipe_query_result', None)
        current_step = getattr(state.user_attributes, 'current_step', None)
        started_cooking = getattr(state.user_attributes, 'started_cooking', False)

        if not resume_task:
            current_task = getattr(state.user_attributes, 'current_task')
            list_item_selected = getattr(state.user_attributes, 'list_item_selected', None)
            if current_task is not None: list_item_selected = getattr(state.user_attributes, 'list_item_selected')
            if list_item_selected is None: list_item_selected = get_list_item_selected(state)

            setattr(state.user_attributes, 'list_item_selected', list_item_selected)

            recipe_item = recipe_query_result[list_item_selected]
        else:
            recipe_item = getattr(state.user_attributes, 'recipe', None)

        if started_cooking:
            if current_step == 0:
                if not resume_task:
                    current_step, speak_output, document = self._get_recipe_steps(state, recipe_item, card=True)
                else:
                    current_step, speak_output, document = self._get_recipe_steps(state, recipe_item)
            else:
                current_step, speak_output, document = self._get_recipe_steps(state, recipe_item)
        else:
            speak_output, document = self._get_recipe_overview(state, recipe_item, current_step)

        setattr(state.user_attributes, 'current_step', current_step)
        setattr(state.user_attributes, 'started_cooking', started_cooking)

        if getattr(state.user_attributes, 'global_speak_output'):
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)

        setattr(state.user_attributes, 'last_legal_response', speak_output)

        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if not is_apl_supported:
            return {'response': speak_output}
        else:
            return {'response': speak_output, 'directives': [document.build_document()]}


    # Recipe Overview
    def _get_recipe_overview(self, state, selected_item, current_ingredient):
        """
        Returns response, detail APL document with text and image, and scroll command
        """
        recipe_item = selected_item
        recipe_title = recipe_item.get('title')
        n_steps = len(recipe_item.get('steps'))
        n_ingredients = len(recipe_item.get('ingredients'))

        document = CustomAplDocument('recipe_preview_v2.json')
        data = deepcopy(DATASOURCE.get('overview'))

        data['title'] = recipe_title
        steps_placeholder = "<br><span color='rgba(0,0,0,0)'>==== ==== ==== ====<br>==== ==== ==== ==== ====<br>===== ==== ===== ===== ===== ===== =====</span>"
        data['steps'] = [step.get('text') for step in recipe_item.get('steps')]
        data['steps'][-1] += steps_placeholder
        ingredient_tool_placeholder = [' ', ' ', ' ']
        data['ingredientsAndTools'] = ['<strong>Ingredients & Tools</strong>',] + [ingredient.get('text') for ingredient in recipe_item.get('ingredients')] + ingredient_tool_placeholder

        multimodal_speak_output = f"Great! Before we get started, please be careful when using any tools or equipment. Remember, safety first! OK, {recipe_title} has {n_steps} steps. You can find all ingredients on the screen, or say ingredients to hear them. Once you are ready, just say, start cooking."
        headless_speak_output = f"Great! Before we get started, please be careful when using any tools or equipment. Remember, safety first! OK, {recipe_title} has {n_steps} steps. Say ingredients to hear them. Once you are ready, just say, start cooking."

        speak_output = None
        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if not is_apl_supported: speak_output = headless_speak_output
        else: speak_output = multimodal_speak_output

        if not speak_output: speak_output = headless_speak_output
        
        if getattr(state.user_attributes, 'unsure'):
            setattr(state.user_attributes, 'unsure', False)
            is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
            speak_output = "Sorry, I'm unsure about it. Could you try something else?"

        if getattr(state.user_attributes, 'read_ingredients'):
            setattr(state.user_attributes, 'read_ingredients', False)
            ingredient_list = ", <break time='1s'/> ".join([ingredient.get('text').strip() for ingredient in recipe_item.get('ingredients')])
            speak_output = f"For this recipe, you will need {ingredient_list}."

        document.data = data

        setattr(state.user_attributes, 'recipe', recipe_item)
        setattr(state.user_attributes, 'n_steps', n_steps)
        setattr(state.user_attributes, 'current_task', getattr(state.user_attributes, 'search_query'))
        setattr(state.user_attributes, 'prev_task_domain', getattr(state.user_attributes, 'task_domain'))
        return speak_output, document


    # Recipe Steps
    def _get_recipe_steps(self, selected_item, card=False):
        """
        Returns response, text list APL document with a vertical list of items, and scroll command
        """
        if card: setattr(state.user_attributes, 'send_card', True)
        else: setattr(state.user_attributes, 'send_card', None)

        recipe_item = selected_item
        current_step = state.user_attributes.current_step
        n_steps = len(recipe_item.get('steps'))
        setattr(state.user_attributes, 'recipe', recipe_item)

        step = recipe_item.get('steps')[current_step]
        step_detail = step.get('text').replace("approx.", "approximately").rstrip('. ') + '.'

        document = CustomAplDocument('recipe_steps_v2.json')
        data = deepcopy(DATASOURCE.get('steps'))

        data['title'] = recipe_item.get('title')
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
        
        data['imageSrc'] = recipe_item.get('thumbnail_url')
        data['button1Text'] = 'Overview' if current_step == 0 else 'Previous'
        data['button2Text'] = 'Complete' if current_step == n_steps - 1 else 'Next'
        step_ingredients = get_step_ingredients(step_detail)
        data['ingredients'] = step_ingredients if step_ingredients else ['Not Specified']

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

        return current_step, speak_output, document
