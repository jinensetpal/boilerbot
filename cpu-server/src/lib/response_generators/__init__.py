#!/usr/bin/env python3


from .wikihow_steps import ResponseGeneratorWikihowShowSteps
from .recipe_steps import ResponseGeneratorRecipeShowSteps
from .task_complete import ResponseGeneratorTaskComplete
from .wikihow_query import ResponseGeneratorWikiHowQuery
from .query_confirm import ResponseGeneratorQueryConfirm
from .recipe_query import ResponseGeneratorRecipeQuery
from .query_edit import ResponseGeneratorQueryEdit
from .sensitive import ResponseGeneratorSensitive
from .dangerous import ResponseGeneratorDangerous
from .launch import ResponseGeneratorLaunch 
from .qa import ResponseGeneratorQA


launch_responder = {
    'name': 'LAUNCH_RESPONDER',
    'class': ResponseGeneratorLaunch,
    'url': 'local',
    'paths': ['QUERY_CONFIRM_RESPONDER', 'RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER', 'DANGEROUS_RESPONDER']
}

task_complete_responder = {
    'name': 'TASK_COMPLETE_RESPONDER',
    'class': ResponseGeneratorTaskComplete,
    'url': 'local',
    'paths': ['LAUNCH_RESPONDER']
}

recipe_query_responder = {
    'name': 'RECIPE_QUERY_RESPONDER',
    'class': ResponseGeneratorRecipeQuery,
    'url': 'local',
    'paths': ['RECIPE_SHOW_STEPS_RESPONDER']
}

wikihow_query_responder = {
    'name': 'WIKIHOW_QUERY_RESPONDER',
    'class': ResponseGeneratorWikiHowQuery,
    'url': 'local',
    'paths': ['WIKIHOW_SHOW_STEPS_RESPONDER']
}

recipe_show_steps_responder = {
    'name': 'RECIPE_SHOW_STEPS_RESPONDER',
    'class': ResponseGeneratorRecipeShowSteps,
    'url': 'local',
    'paths': ['RECIPE_SHOW_STEPS_RESPONDER', 'RECIPE_QUERY_RESPONDER', 'TASK_COMPLETE_RESPONDER', 'TIMER_MANAGEMENT_RESPONDER']
}

wikihow_show_steps_responder = {
    'name': 'WIKIHOW_SHOW_STEPS_RESPONDER',
    'class': ResponseGeneratorWikihowShowSteps,
    'url': 'local',
    'paths': ['WIKIHOW_SHOW_STEPS_RESPONDER', 'WIKIHOW_QUERY_RESPONDER', 'VIDEO_RESPONDER', 'TASK_COMPLETE_RESPONDER', 'TIMER_MANAGEMENT_RESPONDER']}

query_edit_responder = {
    'name': 'QUERY_EDIT_RESPONDER',
    'class': ResponseGeneratorQueryEdit,
    'url': 'local',
    'paths': ['QUERY_EDIT_RESPONDER', 'RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER']
}

query_confirm_responder = {
    'name': 'QUERY_CONFIRM_RESPONDER',
    'class': ResponseGeneratorQueryConfirm,
    'url': 'local',
    'paths': ['QUERY_EDIT_RESPONDER', 'RECIPE_QUERY_RESPONDER', 'WIKIHOW_QUERY_RESPONDER']
}

dangerous_responder = {
    'name': 'DANGEROUS_RESPONDER',
    'class': ResponseGeneratorDangerous,
    'url': 'local',
    'paths': ['LAUNCH_RESPONDER']
}

qa_responder = {
    'name': 'QA_RESPONDER',
    'class': ResponseGeneratorQA,
    'url': 'local',
    'paths': ['LAUNCH_RESPONDER']
}

sensitive_responder = {
    'name': 'SENSITIVE_RESPONDER',
    'class': ResponseGeneratorSensitive,
    'url': 'local',
    'paths': ['LAUNCH_RESPONDER']
    }

GENERATORS = [launch_responder, query_confirm_responder, query_edit_responder, task_complete_responder,
       recipe_query_responder, wikihow_query_responder, recipe_show_steps_responder, wikihow_show_steps_responder,
       sensitive_responder, qa_responder, dangerous_responder, query_edit_responder, query_confirm_responder]
