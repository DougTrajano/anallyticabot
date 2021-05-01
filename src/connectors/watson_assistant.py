#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from tryagain import retries
import datetime
import pandas as pd
from src.helper_functions import setup_logger

logger = setup_logger()


class WatsonAssistant:
    def __init__(self, apikey: str, service_endpoint: str, default_skill_id: str = None):
        """
        This class implement a connector with Watson Assistant API.

        Arguments:
        - apikey (str, required): Your apikey to get access on Watson Assistant service.
        - service_endpoint (str, required): The URL to service endpoint that you Watson Assistant are allocated.
        - default_skill_id (str, optional): The skill/worksapce id of your Watson Assistant.
        """

        logger.info({"message": "Initialize WatsonAssistant object."})

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
    def get_workspace(self, skill_id: str = None):
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
                logger.error({"message": "skill_id is missing."})
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        logger.info(
            {"message": "Getting workspace from Watson API.", "skill_id": skill_id})

        response = self.assistant.get_workspace(
            workspace_id=skill_id, export=True).get_result()

        self.watson_workspace = response

        return response

    @retries(max_attempts=3, wait=1.0)
    def add_counterexamples(self, txt: str , skill_id: str = None):
        """
        Add counterexample to Watson Assistant skill.

        Arguments:
        - txt (str, required): The counterexample to be added in Watson Assistant skill.
        - skill_id (str, optional, default will be provided by class): The skill/worksapce id of your Watson Assistant.

        Output:
        - Dict with "success" indicating True or False and Watson Assistant payload: create_counterexample().
        """
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                logger.error({"message": "skill_id is missing."})
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        logger.info({"message": "Adding counterexample to Watson Assistant.",
                      "counterexample": txt, "skill_id": skill_id})

        try:
            response = self.assistant.create_counterexample(
                workspace_id=skill_id, text=txt).get_result()
            response["success"] = True
        except Exception as error:
            logger.error({"message": "Failed to add counterexample to Watson Assistant.",
                           "exception": error, "counterexample": txt, "skill_id": skill_id})
            response = {"success": False, "exception": error}
        
        return response

    @retries(max_attempts=3, wait=1.0)
    def get_counterexamples(self, skill_id: str = None):
        """
        Get counterexamples from Watson Assistant skill.

        Arguments:
        - skill_id (str, optional, default will be provided by class): The skill/worksapce id of your Watson Assistant.

        Output:
        - Dict with "success" indicating True or False and "counterexamples" with Watson Assistant's counterexamples.
        """
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                logger.error({"message": "skill_id is missing."})
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        logger.info(
            {"message": "Getting counterexamples from Watson Assistant.", "skill_id": skill_id})

        try:
            response = self.assistant.list_counterexamples(
                workspace_id=skill_id, page_limit=999).get_result()

            counterexamples = [e["text"] for e in response["counterexamples"]]
            response = {"counterexamples": counterexamples, "success": True}
        except Exception as error:
            logger.error({"message": "Failed to get counterexamples from Watson Assistant.",
                           "exception": error, "skill_id": skill_id})
            response = {"success": False, "exception": error}
        
        return response

    @retries(max_attempts=3, wait=1.0)
    def delete_counterexamples(self, txt: str, skill_id: str = None):
        """
        Delete counterexample from Watson Assistant.

        Arguments:
        - txt (str, required): The counterexample to be deleted.
        - skill_id (str, optional, default will be provided by class): The skill/worksapce id of your Watson Assistant.

        Output:
        - Watson Assistant payload: delete_counterexample().
        """
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                logger.error({"message": "skill_id is missing."})
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        logger.info({"message": "Deleting counterexample from Watson Assistant.",
                      "counterexample": txt, "skill_id": skill_id})

        try:
            response = self.assistant.delete_counterexample(
                workspace_id=skill_id, text=txt).get_result()
            response["success"] = True
        except Exception as error:
            logger.error({"message": "Failed to delete counterexample from Watson Assistant.",
                           "counterexample": txt, "skill_id": skill_id, "exception": error})
            response = {"success": False, "exception": error}
        
        return response

    @retries(max_attempts=3, wait=1.0)
    def check_connection(self, skill_id: str = None):
        """
        Check connection with Watson workspace.

        Arguments:
        - skill_id (str, optional, default will be provided by class): The skill/worksapce id of your Watson Assistant.

        Output:
        - Watson Assistant payload: get_workspace().
        """
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        logger.info(
            {"message": "Checking Watson Assistant connection.", "skill_id": skill_id})

        try:
            response = self.assistant.get_workspace(
                workspace_id=skill_id, export=False).get_result()
        except Exception as error:
            logger.error({"message": "Failed to connect to this Watson Assistant instance.",
                           "exception": error, "skill_id": skill_id})
            response = {"status": "Not Available",
                        "exception": error,
                        "message": "Failed to connect to this Watson Assistant instance."}
        
        return response

    def send_message(self, message: str, skill_id: str = None):
        """
        Check connection with Watson workspace.

        Arguments:
        - message (str, required): The message that needs to be send to Watson.
        - skill_id (str, optional, default will be provided by class): The skill/worksapce id of your Watson Assistant.

        Output:
        - Watson Assistant payload: message().
        """
        # Parameters check
        if skill_id == None:
            if self.default_skill_id == None:
                raise AttributeError("skill_id is missing.")
            else:
                skill_id = self.default_skill_id
        else:
            self.default_skill_id = skill_id

        if not isinstance(message, str):
            logger.error({"message": "message needs to be string."})
            raise ValueError("message needs to be string.")
        if len(message) < 1 or len(message) > 2048:
            logger.error({"message": "message constraints: 1 ≤ length ≤ 2048"})
            raise ValueError("message constraints: 1 ≤ length ≤ 2048")

        logger.info({"message": "Sending message to Watson Assistant.", "skill_id": skill_id, "message": message})

        return self.assistant.message(workspace_id=skill_id,
                                      input={"text": message},
                                      alternate_intents=True).get_result()

    def get_intents(self):
        """
        This function returns a dict with examples and intents.

        Arguments:
        - return_watson (bool): Return as Watson Assistant API provided.

        Output:
        - A dict with "examples" list and "intents" list.
        """

        logger.info({"message": "Getting intents from Watson Assistant."})

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

    def define_query_by_date(self, start_date: datetime.datetime, end_date: datetime.datetime):
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

    def get_logs(self, skill_id: str = None, query: str = None, sort: str = "-request_timestamp", max_logs: int = 5000):
        """

        Arguments:
        - skill_id (str, optional, default will be provided by class): The skill/worksapce id of your Watson Assistant.
        - query (str, optional, default is None and will return logs for last 7 days): The query to be passed to Watson API, see IBM Cloud docs for more details.
        - sort (str, optional, default is "-request_timestamp"): The sort parameter to be passed to Watson API, see IBM Cloud docs for more details.
        - max_logs (int, optional, default is 5000): The max quantity of logs to be collected.

        Output:
        - A list with logs requested.
        """

        if skill_id == None:
            skill_id = self.default_skill_id

        logger.info({"message": "Getting logs from Watson Assistant.", "skill_id": skill_id, "query": query, "sort": sort, "max_logs": max_logs})

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
            logger.error({"message": "You've reached the rate limit of log api, refer to https://www.ibm.com/watson/developercloud/assistant/api/v1/curl.html?curl#list-logs for additional information."})
            raise Exception(
                "You've reached the rate limit of log api, refer to https://www.ibm.com/watson/developercloud/assistant/api/v1/curl.html?curl#list-logs for additional information.")
        except Exception as error:
            logger.error({"message": "Failed to get logs from Watson Assistant.", "exception": error, "skill_id": skill_id, "query": query})
            raise Exception(error)      

        self.watson_logs = logs
        return logs
     
