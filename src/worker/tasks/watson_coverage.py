"""Watson Coverage Task."""
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from worker.tasks.base import TaskBase
from worker.tasks.factory import TaskFactory
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def _get_assistant(url: str, apikey: str, version: str) -> AssistantV2:
    authenticator = IAMAuthenticator(apikey)
    assistant = AssistantV2(
        version=version,
        authenticator=authenticator
    )

    assistant.set_service_url(url)
    return assistant

def _send_message(
        assistant: AssistantV2,
        assistant_id: str,
        user_id: str,
        alternate_intents: bool,
        data: Dict,
        message_key: str) -> Dict:
    """Send message to Watson Assistant asynchronously.
    
    Args:
    - assistant (AssistantV2): Watson Assistant instance.
    - assistant_id (str): Watson Assistant ID.
    - user_id (str): User ID.
    - alternate_intents (bool): Whether to return more than one intent.
    - data (dict): The user data that contains the message_key value.
    - message_key (str): The key of the message in the data.
    
    Returns:
    - The user data with the Watson Assistant response.
    """
    response = assistant.message_stateless(
        assistant_id=assistant_id,
        user_id=user_id,
        input={
            "message_type": "text",
            "text": data[message_key],
            'options': {'alternate_intents': alternate_intents}
        }
    ).get_result()

    for i, intent in enumerate(response["output"]["intents"]):
        data[f"watson_intent_{i}"] = intent["intent"]
        data[f"watson_confidence_{i}"] = intent["confidence"]

    return data

@TaskFactory.register("watson_coverage")
class WatsonCoverage(TaskBase):
    """Watson Coverage Task."""
    _name: str = "watson_coverage"
    _version: str = "1.0"

    def run(self, inputs: Dict[str, str], params: Dict[str, str]) -> Dict:
        """Run Watson Coverage task.
        This task calculates the coverage of Watson Assistant for a given set of examples.
        
        Args:
        - inputs (dict): The inputs for the task.
        - params (dict): The parameters for the task.
        
        Returns:
        - dict: The output of the task.
        """
        self.state.status_desc = "Watson Coverage task is running."
        self.backend.update_task_details(
            task_id=self.state.task_id,
            status=self.state.status,
            status_desc=self.state.status_desc
        )

        assistant = _get_assistant(
            params["watson_url"],
            params["watson_apikey"],
            params["watson_version"]
        )

        with ThreadPoolExecutor() as executor:
            threads = [
                executor.submit(
                    _send_message,
                    assistant,
                    params["watson_assistant_id"],
                    params["watson_user_id"],
                    params.get("watson_alternate_intents", False),
                    item,
                    params.get("watson_example_column", "example")
                )
                for item in inputs["data"]
            ]

        data = []
        with tqdm(total=len(threads)) as pbar:
            for thread in threads:
                data.append(thread.result())
                pbar.update(1)
                self.state.progress = pbar.n / pbar.total
                self.on_step_end()

        # Calculate coverage
        total = len(data)
        coverage = sum(
            1 for item in data
            if (
                "watson_confidence_0" in item
                and item["watson_confidence_0"] >= params.get("threshold", 0.5)
            )
        ) / total

        self.logger.debug(
            {
                "sample_data": data[:5],
                "coverage": coverage
            }
        )

        return {
            "data": data,
            "coverage": coverage
        }
