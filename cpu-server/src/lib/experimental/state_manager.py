#!/usr/bin/env python3

import json


class AttributeDict(dict):
    def __init__(self, state, root=False):
        super().__init__(state)

        if root:
            self['current_state'] = AttributeDict(state.get('current_state', {'directive': []}))
            self['user_attributes'] = AttributeDict(state.get('user_attributes', {}))

        for key in self: 
            if type(self[key]) == dict: self[key] = AttributeDict(self[key])

    def __getattr__(self, key):
        if key not in self: self[key] = AttributeDict({})
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __hash__(self):
        return len(self.keys())

    def render(self):
        return json.loads(json.dumps({key: self[key] for key in self if key != '_id'}))
