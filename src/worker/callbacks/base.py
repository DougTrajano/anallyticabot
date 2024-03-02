"""Base Callback"""
from dataclasses import dataclass
from typing import Dict, Optional
from worker.settings import WorkerSettings


@dataclass
class TaskState:
    """Class for the state of a task."""
    task_id: str
    task_metadata: Optional[Dict] = None
    status: str = "PENDING"
    status_desc: Optional[str] = None
    progress: Optional[float] = None
    outputs: Optional[Dict] = None

@dataclass
class TaskControl:
    """Class for the control of a task."""
    should_task_stop: bool = False

class BaseCallback:
    """Base Callback"""
    def __init__(self):
        self.args = WorkerSettings()

    def on_start(self, state: TaskState, control: TaskControl):
        """On Start"""

    def on_step_start(self, state: TaskState, control: TaskControl):
        """On Step Start"""

    def on_step_end(self, state: TaskState, control: TaskControl):
        """On Step End"""

    def on_success(self, state: TaskState, control: TaskControl):
        """On Success"""

    def on_failure(self, state: TaskState, control: TaskControl):
        """On Failure"""

    def on_end(self, state: TaskState, control: TaskControl):
        """On End"""
