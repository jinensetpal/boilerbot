from sentence_transformers import SentenceTransformer
import numpy as np
import pickle

class SVMClassifier:
    def __init__(self):
        self.clf = pickle.load(open((const.MODELS_DIR / 'new_dangerous.pkl').as_posix(), 'rb'))
        self.model = SentenceTransformer('all-mpnet-base-v2')

    def predict(self, queries):
        es = self.model.encode(queries)
        if type(queries) == list:
            maxes = self.clf.predict_proba(es)
            maxes = [max(m) for m in maxes]
            return self.clf.predict(es), maxes
        es = es.reshape(1,-1)
        return self.clf.predict(es)[0], max(self.clf.predict_proba(es)[0])

clf = SVMClassifier()

def handle_message(msg):
    domain, probability = clf.predict(msg)
    if type(domain) == np.str_: domain = str(domain)
    else: domain = [str(x) for x in domain]
    if type(probability) == np.float64: probability = float(probability)
    else: probability = [float(x) for x in probability]

    return {
        'text': msg,
        'domain': domain,
        'probability': probability
    }

def testClassifier():
    tags = ["safe", "dangerous"]

    test_set = []
    with open((const.DATA_DIR / 'safe.txt').as_posix(), 'r') as f:
        for line in f:
            # append [line, 1] to test_set. make sure to strip the line of whitespaces using strip()
            test_set.append([line.strip(), 1])

    for item in test_set:
        debugInfo = item[0] + "\n" + "Expected: " + tags[item[1]] + " | Predicted: " + handle_message(item[0])['domain']
        print(debugInfo)

testClassifier()
