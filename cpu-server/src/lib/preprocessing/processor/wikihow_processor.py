import json
from lib.preprocessing.doc.wikihow_doc import WikihowDoc

class WikihowProcessor:
    def filter(self, document):
        """ return True is valid else False if not"""
        document = json.loads(document)
        return document['title'] and document['steps']
    

    def document_preprocess(self, document):
        doc = WikihowDoc()
        doc.process(document)
        return doc._to_json()
