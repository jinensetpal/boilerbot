from sentence_transformers import SentenceTransformer
from sklearn.svm import SVC
from src import const
import numpy as np
import pickle

class InstrumentClassifier:
    def __init__(self):
        self.clf = SVC(probability=True)
        self.load()
        self.model = SentenceTransformer('all-mpnet-base-v2')

    def predict(self, queries):
        es = self.model.encode(queries)
        if type(queries) == list:
            maxes = self.clf.predict_proba(es)
            maxes = [max(m) for m in maxes]
            return self.clf.predict(es), maxes
        es = es.reshape(1,-1)
        return self.clf.predict(es)[0], max(self.clf.predict_proba(es)[0])

    def load(self):
        file = open((const.MODELS_DIR / 'request_clf.model').as_posix(), 'rb') 
        self.clf = pickle.load(file)

clf = InstrumentClassifier()

def handle_message(msg):
    domain, probability = clf.predict(msg)
    if type(domain) == np.str_: domain = str(domain)
    else: domain = [str(x) for x in domain]
    if type(probability) == np.float64: probability = float(probability)
    else: probability = [float(x) for x in probability]

    return {
        'domain': domain,
        'probability': probability,
        'noun_phrases': msg
    }
