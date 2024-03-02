"""Base class for a task."""
import re
import uuid
from abc import ABCMeta, abstractmethod
from typing import Dict
from worker.callbacks.base import BaseCallback, TaskState, TaskControl
from worker.callbacks.backend import BackendCallback
from worker.settings import WorkerSettings
from worker.backend import BackendAPI
from common.logger import logger


class TaskBase(metaclass=ABCMeta):
    """Base class for a task."""
    _name: str
    _version = "1.0"
    _id: str
    _cpu: int = 256
    _gpu: bool = False
    _memory_in_mb: int = 512
    _environment: Dict[str, str] = None

    @property
    def name(self):
        """Getter method for the name attribute."""
        return self._name

    @name.setter
    def name(self, value):
        """Setter method for the name attribute."""
        if isinstance(value, str):
            self._name = value
        else:
            raise ValueError("Name must be a string.")

    @property
    def id(self):
        """Getter method for the id attribute."""
        return self._id

    @id.setter
    def id(self, value):
        """Setter method for the id attribute."""
        try:
            uuid.UUID(str(value))
            return True
        except ValueError as exc:
            raise ValueError("ID must be a valid UUID.") from exc

    @property
    def cpu(self):
        """Getter method for the cpu attribute."""
        return self._cpu

    @cpu.setter
    def cpu(self, value):
        """Setter method for the cpu attribute."""
        if isinstance(value, int) and value > 0:
            self._cpu = value
        else:
            raise ValueError("CPU must be a positive integer.")

    @property
    def gpu(self):
        """Getter method for the gpu attribute."""
        return self._gpu

    @gpu.setter
    def gpu(self, value):
        """Setter method for the gpu attribute."""
        if isinstance(value, bool):
            self._gpu = value
        else:
            raise ValueError("GPU must be a boolean.")

    @property
    def memory_in_mb(self):
        """Getter method for the memory_in_mb attribute."""
        return self._memory_in_mb

    @memory_in_mb.setter
    def memory_in_mb(self, value):
        """Setter method for the memory_in_mb attribute."""
        if isinstance(value, int) and value > 0:
            self._memory_in_mb = value
        else:
            raise ValueError("Memory must be a positive integer.")

    @property
    def version(self):
        """Getter method for the version attribute."""
        return self._version

    @version.setter
    def version(self, value):
        """Setter method for the version attribute."""
        if isinstance(value, str) and re.match(r"^\d+\.\d+$", value):
            self._version = value
        else:
            raise ValueError("Version must be in the format of MAJOR.MINOR")

    @property
    def environment(self):
        """Getter method for the environment attribute."""
        return self._environment

    @environment.setter
    def environment(self, value):
        """Setter method for the environment attribute."""
        if isinstance(value, Dict):
            self._environment = value
        else:
            raise ValueError("Environment must be a dictionary.")

    def __init__(
            self, task_id: str,
            callbacks: list[BaseCallback] = None) -> None:
        """Initialize a task."""
        self._id = task_id
        self.callbacks = callbacks or []

        # Add the BackendCallback if it's not in the list of callbacks
        if not any(isinstance(callback, BackendCallback) for callback in self.callbacks):
            self.callbacks.append(BackendCallback())

        self.logger = logger
        self.state = TaskState(task_id=task_id)
        self.control = TaskControl()
        self.backend = BackendAPI(
            base_url=WorkerSettings().API_BASE_ENDPOINT,
            token=WorkerSettings().API_TOKEN
        )

    @abstractmethod
    def run(self, inputs: Dict, params: Dict) -> Dict:
        """Abstract method to run a task.
        
        Args:
        - inputs (Dict): The inputs for the task.
        - params (Dict): The parameters for the task.
        
        Returns:
        - Dict: The output of the task.
        """
        raise NotImplementedError()

    def run_flow(self):
        """Run a task. It's usually called by the task runner."""
        try:
            self.on_start()

            _input = self.backend.get_inputs(
                task_id=self.id
            )

            self.state.outputs = self.run(
                inputs=_input['inputs'],
                params=_input['params']
            )

            self.on_success()
        except Exception as exc:
            self.on_failure(exc)
            raise
        finally:
            self.on_end()

    def on_start(self):
        """Callback for when a task starts."""
        self.state.status = "RUNNING"
        self.state.status_desc = f"{self.name} task is running."
        self.state.progress = 0.0

        for callback in self.callbacks:
            callback.on_start(self.state, self.control)

    def on_success(self):
        """Callback for when a task is successful."""
        self.state.status = "COMPLETED"
        self.state.status_desc = "Task completed successfully."
        self.state.progress = 1.0

        for callback in self.callbacks:
            callback.on_success(self.state, self.control)

    def on_failure(self, exc: Exception):
        """Callback for when a task fails."""
        self.state.status = "FAILED"
        self.state.status_desc = str(exc)

        for callback in self.callbacks:
            callback.on_failure(self.state, self.control)

    def on_end(self):
        """Callback for when a task ends."""
        for callback in self.callbacks:
            callback.on_end(self.state, self.control)

    def on_step_start(self):
        """Callback for when a step starts."""
        for callback in self.callbacks:
            callback.on_step_start(self.state, self.control)

    def on_step_end(self):
        """Callback for when a step ends."""
        for callback in self.callbacks:
            callback.on_step_end(self.state, self.control)
