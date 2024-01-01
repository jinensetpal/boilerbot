import json
from copy import deepcopy

class WikihowDoc:
    def __init__(self):
        self.article_id: str
        self.source_url: str
        self.title: str
        self.thumbnail_url: str
        self.steps: [dict]
        self.tags: [str]
        self.has_parts: bool
        self.part_names: [str]
        self.has_summary: bool
        self.summary_text: str
        self.video_url: str
        self.date: str
        self.rating: float
        self.views: str
    
    @staticmethod
    def human_format(num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
    
    def process(self, document):
        doc_detail = document
        # Article ID
        if doc_detail['articleId']: self.article_id = doc_detail['articleId']
        # Source URL
        if doc_detail['articleUrl']: self.source_url = doc_detail['articleUrl']
        # Title
        if doc_detail['articleTitle']: self.title = doc_detail['articleTitle']
        # Tags
        if doc_detail['topLevelCategories']: self.tags = doc_detail['topLevelCategories']
        # HasParts
        if doc_detail['hasParts']: self.has_parts = doc_detail['hasParts'] 
        else: self.has_parts = False
        # HasSummary
        if doc_detail['hasSummary']: self.has_summary = doc_detail['hasSummary']
        else: self.has_summary = False
        # Date
        date = doc_detail['updated']
        if date:
            year = date[:4]
            month = date[4:6]
            day = date[6:8]
            date = '.'.join([year, month, day])
            self.date = date
        # Rating
        if doc_detail['rating']: self.rating = float(doc_detail['rating'])
        if doc_detail['views']:
            self.views = f"{self.human_format(doc_detail['views'])} Views"
        else:
            self.views = 0

        # Steps Logic
        steps = []
        # sequential order of steps
        # or take the first method of all stand-alones
        if self.has_parts:
            self.part_names = doc_detail['methodsNames']
            for i in range(len(self.part_names)):
                part_title = self.part_names[i]
                part_steps = doc_detail['methods'][i]
                part_imgs = doc_detail['methodsImages'][i]
                for j in range(len(part_steps)):
                    text = part_steps[j]
                    img = part_imgs[j]

                    sub_steptext = self.get_sub_steptext(text)
                    for j in range(len(sub_steptext)):
                        steps.append({'part': part_title, 'text': sub_steptext[j], 'image': img})
            self.steps = steps
            self.thumbnail_url = steps[-1]['image']
        else:
            method = doc_detail['methods'][0]
            for i in range(len(method)):
                text = method[i]
                img = doc_detail['methodsImages'][0][i]

                sub_steptext = self.get_sub_steptext(text)
                for j in range(len(sub_steptext)):
                    steps.append({'text': sub_steptext[j], 'image': img})
            self.steps = steps
            self.thumbnail_url = steps[-1]['image']
        
        # Summary Text
        if self.has_summary: self.summary_text = doc_detail['summaryText']
        # Video URL
        if doc_detail['summaryVideoUrl']: self.video_url = doc_detail['summaryVideoUrl']
    

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
