import json
from lib.preprocessing.doc.wholefoods_doc import WholefoodsDoc

class WholefoodsProcessor:
    def filter(self, document):
        """ return True is valid else False if not"""
        document = json.loads(document)
        return document['title'] and document['steps']

    def document_preprocess(self, document):
        doc = WholefoodsDoc()
        doc.process(document)
        return doc._to_json()
