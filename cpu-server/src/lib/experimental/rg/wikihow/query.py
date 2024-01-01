import random
from time import sleep
from copy import deepcopy

from lib.utils import get_list_item_selected

from lib.apl.custom_apl_handler import CustomAplDocument
from lib.remote_module.modules import search_wikihow_db
from lib.preprocessing.doc_utils import get_taskmaps
from lib.const import *

DATASOURCE = {
    "wikihow_results": {
        "suggested": [],
        "results": [],
        "backgroundImage": "https://boilerbot-media-assets.s3.us-east-2.amazonaws.com/purebg.png"
    }
}

class ResponseGeneratorWikiHowQuery:
    def execute(self, state):
        """
        Search for "how" questions in wikiHow and display an image list of query results
        """
        is_apl_supported = state.current_state.supported_interfaces.get('apl', False)
        search_query = getattr(state.user_attributes, 'search_query', None)
        
        
        # Add a default DIY query
        if {'d. i. y.'}.intersection(set(search_query.split())):
            search_query = "how to make a paper airplane"
            
        # Add a default home improvement query
        if {'improvement', 'home improvement'}.intersection(set(search_query.split())):
            search_query = "how to paint a carpeted room"
        
        setattr(state.user_attributes, 'search_query', search_query)
        
        # local db search
        top_k = 25

        if (getattr(state.user_attributes, 'current_task') != search_query or getattr(state.user_attributes, 'wikihow_query_result') is None) and getattr(state.user_attributes, 'global_speak_output') is None:
            wikihow_query_result = search_wikihow_db(search_query, top_k)
            wikihow_rst = [item for item in wikihow_query_result]
            wikihow_taskmap_result = get_taskmaps(wikihow_rst, 'DIY')
        else:
            wikihow_taskmap_result = getattr(state.user_attributes, 'wikihow_query_result')

        
        # more results
        result_range = getattr(state.user_attributes, 'result_range')
        if not result_range: result_range = [0, 5]
        range_min, range_max = result_range[0], result_range[1]
        if getattr(state.user_attributes, 'more_results', False):
            range_min += 5
            range_max += 5
            setattr(state.user_attributes, 'result_range', [range_min, range_max])
            setattr(state.user_attributes, 'global_speak_output', random.choice(MORE_RESULT_SPEAK_OUTPUTS))

        # Save the query result to the state manager
        self._set_recipe_query_user_attributes(state, wikihow_taskmap_result)

        # Check whether device is APL supported or not
        # If device is not APL supported, we should return only voice response
        if not is_apl_supported:
            speak_output = self._get_wikihow_query_speak_output(state, wikihow_taskmap_result, is_apl_supported, range_min, range_max)
            return {"response": speak_output}
        else:
            speak_output, document = self._get_wikihow_query_document(state, wikihow_taskmap_result, is_apl_supported, range_min, range_max)
            return {"response": speak_output, "directives": [document.build_document()]}

    def _get_wikihow_query_speak_output(self, state, wikihow_taskmap_result, is_apl_supported, range_min, range_max):
        num_results = len(wikihow_taskmap_result)
        if num_results == 0:
            speak_output = f"Sorry, I couldn't find any relevant results. Let's try another question."
            setattr(state.user_attributes, 'new_search', True)
        else:
            speak_output = f"I found a couple of options from Wikihow! Say the option number to select it."

            if state.current_state.is_experiment == True:
                speak_output = f"I found {num_results} great results in Wikihow. You can tell me the option number to proceed."
            
            if getattr(state.user_attributes, 'more_results', False):
                setattr(state.user_attributes, 'more_results', None)
                speak_output = getattr(state.user_attributes, 'global_speak_output')
                setattr(state.user_attributes, 'global_speak_output', None)
            
            candidate_len = 5 if is_apl_supported else 3

            for i in range(range_min, min(range_max, range_min+candidate_len)):
                if i >= num_results:
                    break
                speak_output += f" Option {str(i%(candidate_len)+1)} is {wikihow_taskmap_result[i].get('title')}"
                
                if not is_apl_supported:
                    speak_output += f" with {len(wikihow_taskmap_result[i].get('steps'))} steps"
                else:
                    speak_output += "."
                
            speak_output += " Which option would you like?"

        if getattr(state.user_attributes, 'global_speak_output') is not None:
            speak_output = getattr(state.user_attributes, 'global_speak_output')
            setattr(state.user_attributes, 'global_speak_output', None)

        return speak_output

    def _get_wikihow_query_document(self, state, wikihow_taskmap_result, is_apl_supported, range_min, range_max):
        num_results = len(wikihow_taskmap_result)

        document = CustomAplDocument('wikihow_results_v2.json')
        data = deepcopy(DATASOURCE.get('wikihow_results'))

        # wikihow results only show first 5
        for i in range(range_min, min(range_max, range_min+5)):
            if i >= num_results:
                break

            title = ' '.join([word.title() if word not in WIKIHOW_STOPWORDS else word for word in wikihow_taskmap_result[i].get('title').replace('How to ', '').split()])
            rating_ratio = wikihow_taskmap_result[i].get('rating') * 5 / 100
            n_steps = len(wikihow_taskmap_result[i].get('steps'))
            total_steps = f"{n_steps} Step" if n_steps == 1 else f"{n_steps} Steps"

            data['results'].append({
                "idx": i+1,
                "title": f"{str(i%(range_max-range_min)+1)}. {title}", 
                "image": wikihow_taskmap_result[i].get('thumbnail_url'), 
                "ratingNumber": rating_ratio, 
                "totalSteps": total_steps,
                "totalViews": wikihow_taskmap_result[i].get('views')
            })

        data['results_len'] = len(data.get('results'))

        # speak_output
        speak_output = self._get_wikihow_query_speak_output(state, wikihow_taskmap_result, is_apl_supported, range_min, range_max)

        document.data = data
        setattr(state.user_attributes, 'last_legal_response', speak_output)
        return speak_output, document

    def _set_recipe_query_user_attributes(self, state, wikihow_query_result):
        setattr(state.user_attributes, 'wikihow_query_result', wikihow_query_result)
        setattr(state.user_attributes, 'task_domain', 'DIY')
        setattr(state.user_attributes, 'recipe_query_result', None)
        setattr(state.user_attributes, 'current_task', None)
        setattr(state.user_attributes, 'current_step', None)
        setattr(state.user_attributes, 'list_item_selected', None)
        setattr(state.user_attributes, 'started_cooking', None)
        setattr(state.user_attributes, 'wikihow_video', None)
        setattr(state.user_attributes, 'launch_page', None)

