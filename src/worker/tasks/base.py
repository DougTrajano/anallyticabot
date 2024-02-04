"""Base class for a task."""
import sys
import re
import uuid
from abc import ABCMeta, abstractmethod
from typing import Dict
from worker.callbacks.base import Callback


class TaskBase(metaclass=ABCMeta):
    """Base class for a task."""
    _name: str
    _version = "1.0"
    _id: str
    _cpu: int = 256
    _memory: int = 512
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
    def memory(self):
        """Getter method for the memory attribute."""
        return self._memory

    @memory.setter
    def memory(self, value):
        """Setter method for the memory attribute."""
        if isinstance(value, int) and value > 0:
            self._memory = value
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
            callbacks: list[Callback] = None,
            **kwargs) -> None:
        """Initialize a task."""
        self._id = task_id
        self.callbacks = callbacks or []
        self.kwargs = kwargs

    @abstractmethod
    def run(self, **kwargs) -> None:
        """Abstract method to run a task."""
        raise NotImplementedError()

    def on_start(self):
        """Callback for when a task starts."""
        for callback in self.callbacks:
            callback.on_start()

    def on_success(self, retval, task_id, kwargs):
        """Callback for when a task is successful."""
        for callback in self.callbacks:
            callback.on_success(retval, task_id, kwargs)

    def on_failure(self, exc, task_id, kwargs, einfo):
        """Callback for when a task fails."""
        for callback in self.callbacks:
            callback.on_failure(exc, task_id, kwargs, einfo)

    def update_task_status(self, task_id, status):
        """Update task status."""
        for callback in self.callbacks:
            callback.update_task_status(task_id, status)

    def _run(self, **kwargs):
        """Run a task."""
        self.on_start()
        try:
            retval = self.run(**kwargs)
            self.on_success(retval, self.id, kwargs)
        except Exception as exc:
            self.on_failure(exc, self.id, kwargs, sys.exc_info())
            raise
        finally:
            self.update_task_status(self.id, "SUCCESS")
        return retval
    