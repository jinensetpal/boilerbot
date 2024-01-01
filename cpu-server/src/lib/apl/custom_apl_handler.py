from lib.const import AplTemplateConstants
from pathlib import Path
import json


class CustomAplDocument:
    def __init__(self, filename):
        self.document = {AplTemplateConstants.document_key: {
            "type": "APL",
            "version": "1.6",
            "import": [
                {
                    "name": "alexa-layouts",
                    "version": "1.5.0"
                    }
                ]}}
        self.default_template = dict()
        self.main_template = dict()
        self.datasources = dict()
        self.document["type"] = "Alexa.Presentation.APL.RenderDocument"
        self.token = ''
        self.data = dict()

        file = json.load(open((Path(__file__).parent.parent / 'apl' / 'jsons' / filename).as_posix(), 'r'))
        self.document[AplTemplateConstants.document_key].update(file)
        self.token = 'documentToken'
        self.document['type'] = 'Alexa.Presentation.APL.RenderDocument'
        self.default_template.update(file.get('mainTemplate', {}))
        self.main_template.update(file.get('mainTemplate', {}))


    def _update_document_with_datasources(self, data):
        self.datasources.update({AplTemplateConstants.data_key: data})
        data_sources = {AplTemplateConstants.datasources_key: self.datasources}
        self.document.update(data_sources)


    def build_document(self):
        self._update_document_with_datasources(self.data)
        return self.document
