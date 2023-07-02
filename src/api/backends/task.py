from typing import Any, Dict
from worker.tasks.factory import TaskFactory

class TaskCreator(object):
    def __init__(self, task_name: str, task_args: Dict[str, Any]):
        self.task_name = task_name
        self.task_args = task_args

    def is_task_registered(self):
        """Check if task_name is registered in TaskFactory
        
        Returns:
        - bool: True if task_name is registered in TaskFactory, False otherwise.
        """
        return self.task_name in TaskFactory.registry.keys()
    