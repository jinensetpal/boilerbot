import json
import random
from copy import deepcopy

class WholefoodsDoc:
    def __init__(self):
        self.recipe_id: str
        self.source_url: str
        self.authors: [str]
        self.title: str
        self.thumbnail_url: str
        self.steps: [dict]
        self.ingredients: [dict]
        self.tools: [dict]
        self.tags: [str]
        self.video_url: str
        self.rating_val: float
        self.rating_count: int
        self.difficulty: str
        self.servings: int
        self.diets: [str]
        self.meals: [str]
        self.courses: [str]
        self.occasions: [str]

    
    def process(self, document):
        # Recipe ID
        if document['title']: self.title = document['title']

        # Steps
        if document['steps']: self.steps = document['steps']

    def _to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    # parse extra long step text into sub steps. Return a list of sub steps
    def get_sub_steptext(self, steptext):
        step_max_length = 100
        cur_sub_step = ""
        res = []
        sentences = steptext.split(". ")

        for i in range(len(sentences)):
            cur_sub_step += sentences[i].rstrip('. ').strip() + ". "
            if len(cur_sub_step) > step_max_length:
                res.append(deepcopy(cur_sub_step.strip()))
                cur_sub_step = ""
        
        if len(cur_sub_step) > 0:
            res.append(deepcopy(cur_sub_step.strip()))
        return res
