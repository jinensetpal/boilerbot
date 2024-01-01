#!/usr/bin/env python3


from lib.apl.custom_apl_handler import CustomAplDocument
from copy import deepcopy
from lib.const import *
import random


class ResponseGeneratorQueryConfirm:
    """
        Query confirmation page for users to edit/confirm what they want to do.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {
            "userInput": "",
            "button1Text": "Edit",
            "button2Text": "Confirm",
            "requestType": "",
            "recipe": {
                "ingredientsAndTools": {
                    "include": [],
                    "exclude": []
                },
                "dietaryFilters": [],
                "mealType": ""
            }
        }

    def add_strike(self, data):
        return f"<strike>{data}</strike>"
    
    def add_span(self, data):
        return f"<span color='#2fa74d'>{data}</span>"

    def execute(self, state):
        text = getattr(state.user_attributes, 'search_query')
        domain = getattr(state.user_attributes, 'task_domain')
        search_request = getattr(state.user_attributes, 'search_request')
    
        request = deepcopy(DEFAULT_QUERY) if domain == 'COOK' else deepcopy(DEFAULT_WIKIHOW_QUERY)
        request.update(search_request)
        search_request = request

        speak_output = None

        document = CustomAplDocument('confirm_request_v2.json')
        if domain == 'COOK':
            include, exclude = [], []
            hinclude, hexclude = [], []
            for item in search_request.get('ingredients'):
                if item.get('excluded'): exclude.append(self.add_strike(item.get('name')))
                else: include.append(self.add_span(item.get('name')))
                if item.get('excluded'): hexclude.append(item.get('name'))
                else: hinclude.append(item.get('name'))
            
            userInput = []
            for token in text.split():
                if self.add_strike(token) in exclude:
                    userInput.append(f"<span color='red'>{token}</span>")
                elif self.add_span(token) in include:
                    userInput.append(f"<span color='green'>{token}</span>")
                else:
                    userInput.append(token)

            self.data['userInput'] = ' '.join(userInput)
            self.data['requestType'] = REQUEST_MAP.get(domain) if domain else 'Other'
            self.data['recipe']['ingredientsAndTools']['include'] = include if include else ['Nothing to include']
            self.data['recipe']['ingredientsAndTools']['exclude'] = exclude if exclude else ['Nothing to exclude']
            self.data['recipe']['dietaryFilters'] = search_request.get('dietaryFilters') if search_request.get('dietaryFilters') else ['Any']
            self.data['recipe']['mealType'] = search_request.get('mealType') if search_request.get('mealType') else 'Any'

            dish_out = "a recipe for " + search_request['dishName']
            dietary_out = ""
            includes_out = ""
            excludes_out = ""
            dietary_out += ', '.join(search_request['dietaryFilters'])
            includes_out += ', '.join(hinclude)
            excludes_out += ', '.join(hexclude)
            
            ## so if the lengths of the lists are greater than 0, then add them to the final string
            if len(dietary_out) > 0:
                dietary_out = ", which has the following dietary styles: " + dietary_out
            if len(includes_out) > 0:
                includes_out = ", including the following: " + includes_out
            if len(excludes_out) > 0:
                excludes_out = ", excluding the following: " + excludes_out
            confirm_out = "Did I get it right? Say edit to make changes, or confirm to search for recipes."
            
            is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
            if is_apl_supported: speak_output = f"Here\'s what I understood. {confirm_out}"
            else: speak_output = f"Here\'s what I understood: {dish_out}, which has the following dietary styles: {dietary_out}, including: {includes_out}, excluding: {excludes_out}. {confirm_out}"

        
        if getattr(state.user_attributes, 'global_speak_output'):
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)

        document.data = self.data
        setattr(state.user_attributes, 'last_legal_response', speak_output)
        
        # APL support dependent return clause
        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        if is_apl_supported:  return {"response": speak_output, "directives": [document.build_document()]}
        else: return {"response": speak_output}
