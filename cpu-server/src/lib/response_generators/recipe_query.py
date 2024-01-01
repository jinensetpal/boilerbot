#!/usr/bin/env python3

from lib.apl.custom_apl_handler import CustomAplDocument
from lib.preprocessing.doc_utils import get_taskmaps
from lib.remote_module.modules import search_recipes
from lib.utils import get_list_item_selected
from collections import Counter
from copy import deepcopy
from lib.const import *
import random


DATASOURCE = {
    "recipe_results": {
        "suggested": [],
        "results": [],
        "backgroundImage": "https://boilerbot-media-assets.s3.us-east-2.amazonaws.com/purebg.png"
    }
}

TOP_K = 25

class ResponseGeneratorRecipeQuery:
    """
    Search for recipes and display an image list of query results
    """
    def execute(self, state):
        search_request = getattr(state.user_attributes, 'search_request', None)
        search_query = getattr(state.user_attributes, 'search_query', None)
        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)

        # decide where to load results
        if getattr(state.user_attributes, 'special_event'):
            recipe_taskmap_result = getattr(state.user_attributes, 'recipe_query_result')
        elif (getattr(state.user_attributes, 'current_task') != search_query or getattr(state.user_attributes, 'recipe_query_result') is None) and getattr(state.user_attributes, 'global_speak_output') is None:
            recipe_query_result = search_recipes(search_request, TOP_K)
            recipe_taskmap_result = []
            if recipe_query_result:
                recipe_taskmap_result = get_taskmaps(recipe_query_result.get('documents'), 'COOK')
        else:
            recipe_taskmap_result = getattr(state.user_attributes, 'recipe_query_result')
        
        # more results
        result_range = getattr(state.user_attributes, 'result_range')
        if not result_range: result_range = [0, 5] if is_apl_supported else [0, 3]
        range_min, range_max = result_range[0], result_range[1]
        if getattr(state.user_attributes, 'more_results', False):
            range_min += 5 if is_apl_supported else 3
            range_max += 5 if is_apl_supported else 3
            setattr(state.user_attributes, 'result_range', [range_min, range_max])
            setattr(state.user_attributes, 'global_speak_output', random.choice(MORE_RESULT_SPEAK_OUTPUTS))

        self._set_recipe_query_user_attributes(state, recipe_taskmap_result)

        # apply filter
        if getattr(state.user_attributes, 'recipe_filter', None) is not None:
            recipe_taskmap_result = self._get_filtered_recipe(recipe_taskmap_result)
        
        # render data
        if not is_apl_supported:
            speak_output = self._get_recipe_query_document(state, recipe_taskmap_result, is_apl_supported, range_min, range_max)
            return {"response": speak_output}
        else:
            speak_output, document = self._get_recipe_query_document(state, recipe_taskmap_result, is_apl_supported, range_min, range_max)
            return {"response": speak_output, "directives": [document.build_document()]}


    def _get_filtered_recipe(self, state, recipe_taskmap_result):
        '''
        apply filter to results
        '''
        filtered_results = []
        active_filter = getattr(state.user_attributes, 'recipe_filter')

        for recipe in recipe_taskmap_result:
            if recipe.get('tags') is None:
                continue
            if active_filter in recipe.get('tags'):
                filtered_results.append(recipe)

        return filtered_results


    def _get_recipe_query_speak_output(self, state, recipe_taskmap_result, is_apl_supported, range_min, range_max):
        num_results = len(recipe_taskmap_result)
        if num_results == 0:
            speak_output = f"Sorry, I couldn't find any relevant results. Let's try another question."
            setattr(state.user_attributes, 'new_search', True)
        else:
            speak_output = f"Here is what I found in RecipeNLG. Say option number to select."
            if getattr(state.user_attributes, 'more_results', False):
                print("Showing more results")
                setattr(state.user_attributes, 'more_results', None)
                speak_output = getattr(state.user_attributes, 'global_speak_output')
                setattr(state.user_attributes, 'global_speak_output', None)

            candidate_len = 5 if is_apl_supported else 3

            for i in range(range_min, min(range_max, range_min+candidate_len)):
                if i >= num_results:
                    break
                speak_output += f" Option {str(i%candidate_len+1)} is {recipe_taskmap_result[i].get('title')}"
                
                if not is_apl_supported:
                    speak_output += f" with {len(recipe_taskmap_result[i].get('steps'))} steps"
                else:
                    speak_output += "."
            speak_output += " Which option would you like?"

        if getattr(state.user_attributes, 'global_speak_output') is not None:
            print("Global speak output detected")
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)

        return speak_output.strip()

    def _get_recipe_query_document(self, state, recipe_taskmap_result, is_apl_supported, range_min, range_max):
        num_results = len(recipe_taskmap_result)

        if not is_apl_supported:
            return self._get_recipe_query_speak_output(state, recipe_taskmap_result, is_apl_supported, range_min, range_max)
        else:
            document = CustomAplDocument('recipe_results_v2.json')
            data = deepcopy(DATASOURCE.get('recipe_results'))
            tags = []

            for i in range(range_min, min(range_max, range_min+5)):
                if i >= num_results:
                    break
                if recipe_taskmap_result[i].get('difficulty') is not None: diff_level = f" | {recipe_taskmap_result[i].get('difficulty').title()} Level"
                else: diff_level = ''

                data['results'].append({
                    "idx": i+1,
                    "title": f"{str(i%(range_max-range_min)+1)}. {recipe_taskmap_result[i].get('title')}", 
                    "image": recipe_taskmap_result[i].get('thumbnail_url'), 
                    "ratingNumber": recipe_taskmap_result[i].get('rating_val') or 0, 
                    "ratingText": f"{recipe_taskmap_result[i].get('rating_count')} ratings{diff_level}" if recipe_taskmap_result[i].get('rating_count') else f"Newly Added{diff_level}"
                })

                if recipe_taskmap_result[i].get('tags') is not None:
                    tags.extend(recipe_taskmap_result[i].get('tags'))
            data['results_len'] = len(data.get('results'))

            # filter buttons
            # uncheck -> ic_add
            # checked -> ic_done_inline
            top_fitlers = Counter(tags).most_common(2)
            active_filter = getattr(state.user_attributes, 'recipe_filter')

            for i in range(len(top_fitlers)):
                button_icon = 'ic_done_inline' if active_filter == top_fitlers[i][0] else 'ic_add'
                button_intent = "RESET" if active_filter == top_fitlers[i][0] else f"INTENT.Filter_{top_fitlers[i][0]}"

                data['suggested'].append({
                    "buttonIconSource": button_icon,
                    "buttonText": top_fitlers[i][0].title(),
                    "primaryAction": [
                        {
                            "type": "SendEvent",
                            "arguments": [button_intent]
                        }
                    ]
                })
            
            # speak_output
            speak_output = self._get_recipe_query_speak_output(state, recipe_taskmap_result, is_apl_supported, range_min, range_max)
            document.data = data
            setattr(state.user_attributes, 'last_legal_response', speak_output)
            
            return speak_output, document

    def _set_recipe_query_user_attributes(self, state, recipe_taskmap_result):
        setattr(state.user_attributes, 'recipe_query_result', recipe_taskmap_result)
        setattr(state.user_attributes, 'task_domain', 'COOK')
        setattr(state.user_attributes, 'wikihow_query_result', None)
        setattr(state.user_attributes, 'current_task', None)
        setattr(state.user_attributes, 'current_step', None)
        setattr(state.user_attributes, 'list_item_selected', None)
        setattr(state.user_attributes, 'started_cooking', None)
        setattr(state.user_attributes, 'wikihow_video', None)
        setattr(state.user_attributes, 'launch_page', None)
