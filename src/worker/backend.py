"""This module contains the BackendAPI class, which is used to interact with the backend API."""
from typing import Any, Dict
import requests
from common.logger import logger


class BackendAPI:
    """Class for interacting with the backend API."""
    def __init__(self, base_url: str, token: str = None, timeout: int = 60):
        """Constructor method for the BackendAPI class.

        Args:
        - base_url (str): The base URL for the API.
        - token (str): The token for the API.
        - timeout (int): The timeout for requests in seconds.
        """
        self.base_url = base_url
        self._token = token
        self.timeout = timeout

    def _get_headers(self):
        """Get the headers for requests.

        Returns:
        - dict: The headers for requests.
        """
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def get_task_metadata(self, task_id: str):
        """Get the metadata for a task.

        Args:
        - task_id (str): The ID of the task.

        Returns:
        - dict: The metadata for the task.
        """
        logger.debug("Getting metadata for task %s", task_id)
        url = f"{self.base_url}/tasks/{task_id}"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        logger.debug("Got metadata for task %s", task_id)
        return response.json()

    def get_inputs(self, task_id: str):
        """Get the inputs for a task.

        Args:
        - task_id (str): The ID of the task.

        Returns:
        - dict: The input for the task.
        """
        logger.debug("Getting inputs for task %s", task_id)
        url = f"{self.base_url}/tasks/{task_id}/inputs"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        logger.debug("Got input for task %s", task_id)
        return response.json()

    def set_outputs(self, task_id: str, outputs: Dict[str, Any]):
        """Set the output for a task.

        Args:
        - task_id (str): The ID of the task.
        - output (dict): The output for the task.
        """
        logger.debug("Setting output for task %s", task_id)
        url = f"{self.base_url}/tasks/{task_id}/outputs"
        headers = self._get_headers()

        response = requests.post(
            url,
            headers=headers,
            json={"outputs": outputs},
            timeout=self.timeout
        )

        response.raise_for_status()
        logger.debug("Set output for task %s", task_id)
        return response.json()

    def update_task_details(self, task_id: str, **data):
        """Update the status for a task.

        Args:
        - task_id (str): The ID of the task.
        - data (dict): The details to update.
        
        Returns:
        - dict: The updated task details.
        """
        logger.debug("Updating status for task %s", task_id)
        url = f"{self.base_url}/tasks/{task_id}"
        headers = self._get_headers()
        response = requests.put(url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        logger.debug("Status for task %s updated", task_id)
        return response.json()
