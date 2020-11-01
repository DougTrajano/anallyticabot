#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from tryagain import retries
import datetime
import pandas as pd


class WatsonAssistant:
    def __init__(self, apikey, service_endpoint, default_skill_id=None):
        """
        This class implement a connector with Watson Assistant API.

        Arguments:
        - apikey (str, required): Your apikey to get access on Watson Assistant service.
        - service_endpoint (str, required): The URL to service endpoint that you Watson Assistant are allocated.
        - default_skill_id (str, optional): The skill/worksapce id of your Watson Assistant.
        """
        self.apikey = apikey
        self.version = "2020-04-01"
        self.service_endpoint = service_endpoint
        self.default_skill_id = default_skill_id
        self.assistant = self.load_service()
        self.watson_workspace = None
        self.watson_logs = None

    def load_service(self):
        """
        This functon instantiate a Watson Assistant service object.

        Arguments:
        All arguments are passed in class level.

        Output:
        - Watson Assistant's service object.
        """
        authenticator = IAMAuthenticator(self.apikey)
        assistant = AssistantV1(version=self.version,
                                authenticator=authenticator)
        assistant.set_service_url(self.service_endpoint)
        self.assistant = assistant
        return assistant

    @retries(max_attempts=3, wait=1.0)
    def get_workspace(self, skill_id=None):
        """
        This function return the Watson workspace.

        Arguments:
        - skill_id (str, optional, default will be provided by class): The skill/worksapce id of your Watson Assistant.
        - export (bool, optional, default is True): export parameter to watson API.

        Output:
        - Watson Assistant's data as dict object.
        """
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        response = self.assistant.get_workspace(
            workspace_id=skill_id, export=True).get_result()

        self.watson_workspace = response

        return response

    def add_counterexamples(self, txt, skill_id=None):
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        try:
            response = self.assistant.create_counterexample(
                workspace_id=skill_id, text=txt).get_result()
            response["success"] = True
        except:
            response = {"success": False}
        return response

    def get_counterexamples(self, skill_id=None):
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        try:
            response = self.assistant.list_counterexamples(
                workspace_id=skill_id, page_limit=999).get_result()

            counterexamples = [e["text"] for e in response["counterexamples"]]
            response = {"counterexamples": counterexamples, "success": True}
        except:
            response = {"success": False}
        finally:
            return response

    def delete_counterexamples(self, txt, skill_id=None):
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        try:
            response = self.assistant.delete_counterexample(
                workspace_id=skill_id, text=txt).get_result()
            response["success"] = True
        except:
            response = {"success": False}
        finally:
            return response

    def check_connection(self, skill_id=None):
        """
        Check connection with Watson workspace.

        Arguments:
        - skill_id (str, optional, default will be provided by class): The skill/worksapce id of your Watson Assistant.

        Output:
        - True or False
        """
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        try:
            response = self.assistant.get_workspace(
                workspace_id=skill_id, export=False).get_result()
        except:
            response = {"status": "Not Available",
                        "message": "Failed to connect to this Watson Assistant instance."}
        finally:
            return response

    def get_intents(self):
        """
        This function returns a dict with examples and intents.

        Arguments:
        - return_watson (bool): Return as Watson Assistant API provided.

        Output:
        - A dict with "examples" list and "intents" list.
        """
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

    def define_query_by_date(self, start_date, end_date):
        """
        Helper function to create a query to Watson API based on date ranges.

        Arguments:
        - start_date (pandas.TimeStamp or datetime.datetime, required):
        - end_date (pandas.TimeStamp or datetime.datetime, required):

        Output:
        - Watson API query as str object.
        """

        if isinstance(start_date, pd.Timestamp):
            start_date = start_date.to_pydatetime()
        if isinstance(end_date, pd.Timestamp):
            end_date = end_date.to_pydatetime()

        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        # Query by YYYY-MM-DD
        query = "response_timestamp>={start},response_timestamp<{end}".format(
            start=start_date, end=end_date)
        return query

    def get_logs(self, skill_id=None, query=None, sort="-request_timestamp", max_logs=5000):
        if skill_id == None:
            skill_id = self.default_skill_id

        if query == None:
            # query for last 7 days
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=7)
            query = self.define_query_by_date(start_date, end_date)

        logs = []
        try:
            current_cursor = None
            while max_logs > 0:
                response = self.assistant.list_logs(
                    workspace_id=skill_id,
                    page_limit=500,
                    cursor=current_cursor,
                    sort=sort,
                    filter=query
                ).get_result()

                min_num = min(max_logs, len(response['logs']))
                logs.extend(response['logs'][:min_num])
                max_logs = max_logs - min_num
                current_cursor = None

                if 'pagination' in response:
                    if 'next_cursor' in response['pagination']:
                        current_cursor = response['pagination']['next_cursor']
                    else:
                        break
        except WatsonApiException:
            raise Exception(
                "You've reached the rate limit of log api, refer to https://www.ibm.com/watson/developercloud/assistant/api/v1/curl.html?curl#list-logs for additional information.")
        except Exception as error:
            raise Exception(error)
        finally:
            self.watson_logs = logs
            return logs
