#!/usr/bin/env python3

from injector import inject
import random

from lib.remote_module.modules import classify_domain, get_qa
from lib.selection.action.complete import complete_action
from lib.selection.action.restart import restart_action
from lib.selection.action.proceed import proceed_action
from lib.selection.action.unsure import unsure_action
from lib.selection.action.previous import back_action
from lib.parsing.parsing_utils import get_n_grams
from lib.response_generators import GENERATORS
from lib.selection.steplib import get_step
from lib.utils import cleanup
from lib.const import *

wordlist = WORDLIST

class LogicModule:
    @inject
    def __init__(self, wordlist=wordlist):
        self.graph = self.build(GENERATORS)
        self.wordlist = wordlist
        self.stage = None

    @staticmethod
    def build(generators):
        print('Building graph now...')
        graph_mapping = {'GLOBAL': ['LAUNCH_RESPONDER']}
        for generator in generators:
            paths = generator.get('paths', None)
            if paths: graph_mapping[generator['name']] = {'name': generator['name'], 'paths': paths, 'step': get_step(generator['name'])}
            else: graph_mapping['GLOBAL'].append(generator['name'])
        return graph_mapping

    def step(self, state, text, features) -> None:
        self.stage = self.graph.get(getattr(state.user_attributes, 'curr_stage'), self.graph['LAUNCH_RESPONDER'])
        setattr(state.current_state, 'directive', state.current_state.user_event.get('arguments', []))
        setattr(state.user_attributes, 'log_info', None)
        setattr(state.current_state, 'text', text)

        # Domain result
        domain_result = {}
        domain_clf_layer1 = features.get('domain_clf_layer1')
        if domain_clf_layer1 is None:
            label, score = classify_domain(text, backup=True)
            domain_result['domain'] = label
            domain_result['score'] = score
        else:
            domain_clf_layer2_label, domain_clf_layer2_score = classify_domain(text)
            if (domain_clf_layer2_label in {'CHITCHAT', 'QUESTION', 'UNSUPPORTED_COMMAND'} and domain_clf_layer1['score'] < 0.85) or domain_clf_layer1['score'] < 0.6:
                domain_result['domain'] = domain_clf_layer2_label
                domain_result['score'] = domain_clf_layer2_score
            else:
                domain_result['domain'] = domain_clf_layer1['domain'] if domain_clf_layer1['domain'] != 'GENERAL' else 'CHITCHAT'
                domain_result['score'] = domain_clf_layer1['score']
        print(f"2 Level Domain Clf: Label: {domain_result['domain']}, Score: {domain_result['score']}")
        setattr(state.user_attributes, 'domain_clf', domain_result)
        # precaution when both domain clfs have exceptions
        if not domain_clf_layer1 and (domain_result['domain'] == 'unsure' and domain_result['score'] == 0):
            return [self.graph['LAUNCH_RESPONDER'], self.graph.get(unsure_action(state)) or self.graph['LAUNCH_RESPONDER']]

        # Dangerous/sensitive features
        dangerous_result = features.get('dangerous_clf')
        sensitive_response = features.get('sensitive_clf')

        selected_stage = None
        tokens = get_n_grams(text)
        
        # Global Rules
        if not self.stage or getattr(state.current_state, 'intent', None) in ['LaunchRequestIntent', 'AMAZON.CancelIntent']: 
            selected_stage = self.graph['LAUNCH_RESPONDER']
        elif domain_result['domain'] == 'QUESTION':
            qa_response = get_qa(text)
            if qa_response:
                setattr(state.user_attributes, 'global_speak_output', qa_response)
            selected_stage = self.graph[self.stage.get('name')]
        elif dangerous_result and dangerous_result['category'] != 'good':
            setattr(state.user_attributes, 'dangerous_label', dangerous_result['category'])
            selected_stage = self.graph['DANGEROUS_RESPONDER']
        elif sensitive_response:
            setattr(state.user_attributes, 'sensitive_response', sensitive_response)
            selected_stage = self.graph['SENSITIVE_RESPONDER']
        elif wordlist['restart'].intersection(tokens):
            selected_stage = self.graph[restart_action(state)]
        elif wordlist['repeat'].intersection(tokens):
            selected_stage = self.graph[repeat_action(state)]
        elif wordlist['previous'].intersection(tokens):
            selected_stage = self.graph[back_action(state)]
        elif wordlist['proceed'].intersection(tokens):
            selected_stage = self.graph[proceed_action(state)]
        elif self.stage.get('step', None):
            if self.stage.get('name') in {'DANGEROUS_RESPONDER', 'SENSITIVE_RESPONDER'}:
                prev_stage = getattr(state.user_attributes, 'prev_stage')
                setattr(state.user_attributes, 'curr_stage', prev_stage)
                self.stage = self.graph[prev_stage]
            
            if wordlist['unsupported_command'].intersection(tokens):
                domain_result['domain'] = 'UNSUPPORTED_COMMAND'
            selected_stage = self.graph.get(self.stage['step'](state))
        
        if self.stage.get('name') in {'DANGEROUS_RESPONDER', 'SENSITIVE_RESPONDER'} and selected_stage.get('name') in {'DANGEROUS_RESPONDER', 'SENSITIVE_RESPONDER'}:
            self.stage = selected_stage
            setattr(state.user_attributes, 'curr_stage', self.stage.get('name'))
        else:
            setattr(state.user_attributes, 'prev_stage', self.stage.get('name'))
            self.stage = selected_stage
            setattr(state.user_attributes, 'curr_stage', self.stage.get('name'))
        
        if type(self.stage) == str: self.stage = self.graph[self.stage]
        return [self.graph['LAUNCH_RESPONDER'], self.stage]
