from lib.utils import generate_chat_response_display, get_sensitive_questions_regex
from transformers import pipeline
from lib.const import Prompt
import time
import re


class PIIClassifier:
    def __init__(self):
        self.model = pipeline('token-classification', 'ArunaSaraswathy/bert-finetuned-ner-pii')

    def classify(self, utterance):
        detections = self.model(utterance)
        if len(detections) == 0: return False
        return max([detection['score'] for detection in detections]) > 0.85

class OffensiveSpeechClassifier:
    def __init__(self):
        self.model = pipeline('text-classification', model='cardiffnlp/twitter-roberta-base-offensive')

    def classify(self, utterance):
        return self.model(utterance)[0]['label'] == 'offensive'

class SensitiveClassifierModule:
    def __init__(self):
        self.sensitive_questions_regex = get_sensitive_questions_regex()
        self.offensive_classifier = OffensiveSpeechClassifier()
        self.privacy_classifier = PIIClassifier()

    def execute(self, state, text):
        start = time.time()

        sensitive_result = {}
        if self.offensive_classifier.classify(text) or self.privacy_classifier.classify(text):
            sensitive_result['response'] = Prompt.topic_redirection_prompt
        for question in self.sensitive_questions_regex:
            if any(re.match(q, text) for q in question[0]):
                sensitive_result['response'] = question[1]
                break
        end = time.time()
        print(f"Sensitive Clf Latency: {end - start}s")
        if not text:
            return None

        return {'sensitive_clf': sensitive_result}
