#!/usr/bin/env python3

from lib.remote_module.modules import get_question_clf
import requests

"""
A sample response generator using EVI question answering API with QA classification models.
It calls EVI API to get an answer to an utterance and uses QA classification models to decide whether the response is good or not.
"""

TIMEOUT_IN_MILLIS = 2000
RR_LABEL_GOOD = "1"
RR_LABEL_BAD = "0"
QA_FACTOID_LABEL = "QA_FACTOID_LABEL"
QA_RESPONSE_RELEVANCE_LABEL = "QA_RESPONSE_RELEVANCE_LABEL"

CONFIDENCE_HIGH = 'confidence_high'
CONFIDENCE_MEDIUM = 'confidence_medium'
CONFIDENCE_LOW = 'confidence_low'

# For queries like 'hello', EVI returns a long meaningless string that usually contains a skill ID starting with
# 'skill://'.
# what is the news on corona virus - evi response - Audio: AP News Update COVID-19.mp3
# If any of these are a substring of the EVI response, we discard the response.
# We check for these: (a) ignoring case, (b) ignoring word boundaries (i.e. we just check str.contains()).
RESPONSE_NOT_ALLOWED_SUBSTRINGS = {
    'Alexa,',
    'skill://',
    'Audio:',
    'please say that again',
    'please try that again',
    'catch that',
    'find the answer to the question I heard',
    'I didn’t get that',
    'have an opinion on that',
    'skill',
    'skills',
    'you can',
    'try asking',
    "Here's something I found on",
    'Sorry, I don’t know that'
}

_sessions = requests.Session()


class ResponseGeneratorQA:
    """
    A full QA response generator class Using the EVI and QA models
    """
    def execute(self, state):
        """
        Takes advantage of the punctuation API to and EVI model to answer the first
        question in a user's utterance.
        """
        # Retrieving text from teh state module
        text = state.current_state.text

        # Proceeding with standard EVI querying logic
        evi_response = self._call_evi_service(text)
        fc_response, rr_response = self._call_qa_classification_service(text, evi_response)
        evi_response = self.process_response(evi_response)
        confidence = self.get_confidence(evi_response, fc_response, rr_response, text)
        self.logger.info("QA Confidence: %s", confidence)

        # Only return a response if there is a high confidence that it is the answer
        if confidence == CONFIDENCE_HIGH:
            return evi_response
        return None

    @staticmethod
    def create_qa_service_request(text, response):
        """
        Build a payload for the QA classification service
        """
        request = dict()
        request["turns"] = list()
        request["turns"].append([text, response])
        return request

    def _call_evi_service(self, current_text):
        """
        Call Evi service
        Input is a text. Timeout parameter is optional and the client timeout value is used if it's not set.
        """
        return None

    def _call_qa_classification_service(self, text, response):
        """
        Call the toolkits qa classification service
        """
        return None

    @staticmethod
    def get_confidence(evi_response, fc_response, rr_response, text):
        """
        Get confidence about the appropriateness of EVI response. In real use case, it can be modified to return
        a numeric value that can be used for ranking by custom ranking strategy.
        """
        confidence = CONFIDENCE_LOW
        if evi_response and fc_response:
            confidence = CONFIDENCE_HIGH
        elif evi_response and not fc_response and rr_response == RR_LABEL_GOOD:
            confidence = CONFIDENCE_HIGH
        elif evi_response:
            confidence = CONFIDENCE_MEDIUM

        if confidence == CONFIDENCE_HIGH and not get_question_clf(text):
            confidence = CONFIDENCE_MEDIUM

        return confidence

    @staticmethod
    def process_response(response):
        """
        :param response: check if response contains any not_allowed phrase. Evi qa api sometimes returns not_allowed responses.
         We don't want to use them
        :return:
        """
        if response and any(string.lower() in response.lower() for string in RESPONSE_NOT_ALLOWED_SUBSTRINGS):
            return ""

        return response if response else ''
