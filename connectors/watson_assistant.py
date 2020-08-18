#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from tryagain import retries

class WatsonCon:
    def __init__(self, watson_skill_id=None, watson_apikey=None, watson_version=None):
        self.watson_workspace = None
        self.watson_skill_id = watson_skill_id
        self.watson_apikey = watson_apikey
        self.watson_version = watson_version

    @retries(max_attempts=3, wait=1.0)
    def get_workspace(self, skill_id=None, apikey=None, version=None):

        # Parameters check
        if skill_id == None:
            if self.watson_skill_id == None:
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.watson_skill_id
        else:
            self.watson_skill_id = skill_id

        if apikey == None:
            if self.watson_apikey == None:
                raise AttributeError("apikey is missing.")
            else:
                apikey = self.watson_apikey
        else:
            self.watson_apikey = apikey

        if version == None:
            if self.watson_version == None:
                raise AttributeError("version is missing.")
            else:
                version = self.watson_version
        else:
            self.watson_version = version

        # Get workspace    
        authenticator = IAMAuthenticator(apikey)       
        assistant = AssistantV1(version=version, authenticator=authenticator)
        response = assistant.get_workspace(workspace_id=skill_id, export=True).get_result()
        self.watson_workspace = response
        
        return response # delete it later

    def get_intents(self):
        if self.watson_workspace == None:
            self.get_workspace()
        
        watson_intents = self.watson_workspace["intents"]
        
        examples = []
        intents = []       
        for intent in watson_intents:
            intent_name = intent["intent"]
            for example in intent["examples"]:
                examples.append(example["text"])
                intents.append(intent_name)
                
        return {"examples": examples, "intents": intents}