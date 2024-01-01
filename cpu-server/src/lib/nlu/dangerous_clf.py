#!/usr/bin/env python3

from sentence_transformers import SentenceTransformer
from lib.parsing.parsing_utils import get_n_grams
from pathlib import Path
from lib.const import *
import numpy as np
import pickle
import time


class SVMClassifier:
    def __init__(self):
        self.clf = pickle.load(open(MODELS_DIR / 'svc_model.pkl', 'rb'))
        self.model = SentenceTransformer('all-mpnet-base-v2')

    def predict(self, queries):
        es = self.model.encode(queries)
        if type(queries) == list:
            maxes = self.clf.predict_proba(es)
            maxes = [max(m) for m in maxes]
            return self.clf.predict(es), maxes
        es = es.reshape(1,-1)

        domain, probability = self.clf.predict(es)[0], max(self.clf.predict_proba(es)[0])
        if type(domain) == np.str_: domain = str(domain)
        else: domain = [str(x) for x in domain]
        if type(probability) == np.float64: probability = float(probability)
        else: probability = [float(x) for x in probability]

        return {'category': domain,
                'probability': probability}


class DangerousClassifierModule:
    """
    Domain classifier aims to classify the domain of an utterance with respect to the following categories: COOK, DIY or GENERAL.
    """
    def __init__(self):
        self.domain_clf = SVMClassifier()

    def execute(self, state, current_utterance):
        start = time.time()

        dangerous_result = self.domain_clf.predict(current_utterance)

        dangerous_category_list = {'harmful', 'legal', 'financial', 'medical', 'suicide', 'danger'}
        
        # second level keywords matching detection
        if dangerous_result['category'] == 'good':
            if getattr(state.current_state, 'dangerous', False):
                pred = state.dangerous
                if pred['probability'] > 0.8 and pred['domain'] in dangerous_category_list:
                    dangerous_result['category'] = pred['domain']
                    dangerous_result['score'] = pred['probability']
            if DANGEROUS_LIST.intersection(get_n_grams(current_utterance.lower())):
                dangerous_result['category'] = 'danger'
                dangerous_result['score'] = 1.0

        end = time.time()
        print(f'Dangerous Clf Latency: {end - start}s')
        return {'dangerous_clf': dangerous_result}
