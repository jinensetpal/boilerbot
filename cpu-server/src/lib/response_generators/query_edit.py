#!/usr/bin/env python3

from lib.apl.custom_apl_handler import CustomAplDocument
from copy import deepcopy
from lib.const import *

REQUEST_MAP = {'COOK': 'Cooking',
               'DIY': 'Do-It-Yourself',
               'GENERAL': 'Other'}

class ResponseGeneratorQueryEdit:
    """
        Query edit page for users to update preferences within their selected query.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = {
            "button1Text": "Restart",
            "button2Text": "Confirm"
        }
        hint = "<strong>Try</strong><br> \"add black bean to ingredients\", <br><strong>Or</strong><br> \"set meal type to lunch\""
        self.data = {
            "userInput": hint,
            "button1Text": "Restart",
            "button2Text": "Submit",
            "recipe": {
                "ingredientsAndTools": {
                    "include": [],
                    "exclude": []
                },
                "dietaryFilters": [],
                "mealType": ''
            }
        }

    def add_strike(self, data):
        return f"<strike>{data}</strike>"

    def add_span(self, data):
        return f"<span color='#2fa74d'>{data}</span>"

    def execute(self, state):
        stored_request = getattr(state.user_attributes, 'search_request')
        search_request = deepcopy(DEFAULT_QUERY)
        search_request.update(stored_request)

        speak_output = 'Which item would you like to change? We can update list of ingredients and tools, the number of servings or even the difficulty of the recipe options.'

        if state.current_state.text is not None and 'edit' not in state.current_state.text:
            speak_output = 'Okay, making the change! How about now?'

        include, exclude = [], []
        for item in search_request['ingredients']:
            if item.get('excluded'): exclude.append(self.add_strike(item.get('name')))
            else: include.append(self.add_span(item.get('name')))

        document = CustomAplDocument('edit_request_v2.json')
        
        self.data['recipe']['ingredientsAndTools']['include'] = include if include else ['Nothing to include']
        self.data['recipe']['ingredientsAndTools']['exclude'] = exclude if exclude else ['Nothing to exclude']
        self.data['recipe']['dietaryFilters'] = search_request.get('dietaryFilters') if search_request.get('dietaryFilters') else ['Any']
        self.data['recipe']['mealType'] = search_request.get('mealType') if search_request.get('mealType') else 'Any'

        if getattr(state.user_attributes, 'unsure'):
            setattr(state.user_attributes, 'unsure', False)
            speak_output = "Sorry, I'm unsure about it. Could you try something else?"

        if getattr(state.user_attributes, 'global_speak_output'):
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)
        
        document.data = self.data
        setattr(state.user_attributes, 'last_legal_response', speak_output)

        # APL support dependent return clause
        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if is_apl_supported:
            return {"response": speak_output, "directives": [document.build_document()]}
        else:
            return speak_output
