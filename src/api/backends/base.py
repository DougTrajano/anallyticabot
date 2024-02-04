"""Base class for a backend."""
from worker.tasks.base import TaskBase

class BackendBase:
    """Base class for a backend."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def run(self, task: TaskBase):
        """Runs a task on the backend.

        Args:
        - task (TaskBase): The task to run.
        """
        raise NotImplementedError
    