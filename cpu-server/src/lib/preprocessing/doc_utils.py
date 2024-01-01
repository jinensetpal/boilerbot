import json

from lib.preprocessing.processor.wholefoods_processor import WholefoodsProcessor
from lib.preprocessing.processor.wikihow_processor import WikihowProcessor

# Preprocess the returned recipes into Docs
def get_taskmaps(documents, domain):
    if domain == 'COOK': PROCESSOR = WholefoodsProcessor()
    elif domain == 'DIY': PROCESSOR = WikihowProcessor()
    
    candidate_list = []
    for document in documents:
        doc = PROCESSOR.document_preprocess(document)
        if PROCESSOR.filter(doc): candidate_list.append(json.loads(doc))
    return candidate_list
