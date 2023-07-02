import sys
import re
from abc import ABCMeta, abstractmethod
from worker.callbacks.base import Callback


class Task(metaclass=ABCMeta):
    """Base class for a task."""
    _version = "1.0"

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
        
    def __init__(
            self, id: str,
            callbacks: list[Callback] = [],
            **kwargs) -> None:
        """Constructor"""
        self.id = id
        self.callbacks = callbacks
        self.kwargs = kwargs

    @abstractmethod
    def run(self, **kwargs) -> None:
        """Abstract method to run a task."""
        raise NotImplementedError()

    def on_start(self):
        for callback in self.callbacks:
            callback.on_start()

    def on_success(self, retval, task_id, kwargs):
        for callback in self.callbacks:
            callback.on_success(retval, task_id, kwargs)

    def on_failure(self, exc, task_id, kwargs, einfo):
        for callback in self.callbacks:
            callback.on_failure(exc, task_id, kwargs, einfo)

    def update_task_status(self, task_id, status):
        for callback in self.callbacks:
            callback.update_task_status(task_id, status)

    def _run(self, **kwargs):
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
    