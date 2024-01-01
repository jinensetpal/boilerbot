#!/usr/bin/env python3

from lib.experimental.state_manager import AttributeDict
from fastapi.middleware.cors import CORSMiddleware
from lib.selection.logic_module import LogicModule
from lib.response_generators import GENERATORS
from lib.nlu.driver import execute as nlu
from lib.utils import cleanup, accumulate
from pymongo import MongoClient
from attrs import make_class
from fastapi import FastAPI
import random
import uuid
import time


executor_map = {generator['name']: generator['class']().execute for generator in GENERATORS}
state_table = MongoClient("mongodb://mongo:27017/").database.state_table
logic = LogicModule()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'],
                   allow_methods=['*'], allow_headers=['*'])


@app.post('/')
async def health_check():
    return True


@app.post('/chat')
async def chat(query, uid=None, apl=False):
    start = time.time()

    if not uid: 
        state = {'uid': uuid.uuid4().hex}
        state_table.insert_one(state)
    else: state = state_table.find_one({'uid': uid})
    state = AttributeDict(state, root=True)

    setattr(state.current_state.supported_interfaces, 'apl', apl == 'true')
    response = rank(accumulate(map(lambda responder: {responder['name']: executor_map[responder['step'](state)](state)}, logic.step(state, query, nlu(state, query)))), state)
    state_table.update_one({'uid': uid}, {'$set': state.render()})
    return {**response,
            'uid': state['uid'],
            'time': time.time() - start}


def rank(candidate_responses: dict, state: dict) -> str:
    """
    Sensitive responder is top priority.
    Dangerous responder is the second priority.
    QA responder is the first fallback responder since it only returns a response when it has high confidence.
    Launch responder is the last fallback responder.
    """
    sensitive_response = candidate_responses.pop('SENSITIVE_RESPONDER', None)
    qa_response = candidate_responses.pop('QA_RESPONDER', None)
    launch_response = candidate_responses.pop('LAUNCH_RESPONDER', None)
    dangerous_response = candidate_responses.pop('DANGEROUS_RESPONDER', None)
    request_type = state.current_state.request_type

    if dangerous_response:
        setattr(state.user_attributes, 'curr_stage', 'DANGEROUS_RESPONDER')
        return dangerous_response
    if sensitive_response:
        return sensitive_response
    if candidate_responses:
        # Pick the first available response after removing Sensitive, QA, and Launch responses.
        setattr(state.user_attributes, 'curr_stage', list(candidate_responses.keys())[0])
        return list(candidate_responses.values())[0]
    if request_type == 'LaunchRequest':
        setattr(state.user_attributes, 'curr_stage', 'LAUNCH_RESPONDER')
        cleanup(state)
        return launch_response
    if qa_response:
        return qa_response

    setattr(state.user_attributes, 'curr_stage', 'LAUNCH_RESPONDER')
    cleanup(state)

    return launch_response
