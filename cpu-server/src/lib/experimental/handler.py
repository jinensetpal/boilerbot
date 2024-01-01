#!/usr/bin/env python3

from .rg.launch import ResponseGeneratorLaunch
from .rg.complete import ResponseGeneratorTaskComplete
from .rg.wikihow.query import ResponseGeneratorWikiHowQuery
from .rg.wholefoods.query import ResponseGeneratorRecipeQuery

def get_experimental_config(base):
    print("BETA CONFIG TRIGGERED")
    rgs = {'LAUNCH_RESPONDER': { 'name': 'LAUNCH_RESPONDER',
                                'class': ResponseGeneratorLaunch,
                                'url': 'local',
                                'paths': ['QUERY_CONFIRM_RESPONDER', 'RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER']
                                },
           'TASK_COMPLETE_RESPONDER': {'name': 'TASK_COMPLETE_RESPONDER',
                                       'class': ResponseGeneratorTaskComplete,
                                       'url': 'local',
                                       'paths': ['LAUNCH_RESPONDER']
                                       },
           'RECIPE_QUERY_RESPONDER': {'name': 'RECIPE_QUERY_RESPONDER',
                                      'class': ResponseGeneratorRecipeQuery,
                                      'url': 'local',
                                      'paths': ['RECIPE_SHOW_STEPS_RESPONDER']
                                      },
           'WIKIHOW_QUERY_RESPONDER': {'name': 'WIKIHOW_QUERY_RESPONDER',
                                       'class': ResponseGeneratorWikiHowQuery,
                                       'url': 'local',
                                       'paths': ['WIKIHOW_SHOW_STEPS_RESPONDER']
                                       }}

    for idx, rg in enumerate(base['response_generators']):
        if rg['name'] in ['LAUNCH_RESPONDER', 'TASK_COMPLETE_RESPONDER', 'RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER']:
            base['response_generators'][idx] = rgs[rg['name']]

    return [base,
            {'name': 'redundancy',
             'ratio': 0}]
