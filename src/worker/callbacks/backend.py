"""Backend Callback"""
import datetime
from worker.backend import BackendAPI
from worker.callbacks.base import BaseCallback, TaskState, TaskControl


class BackendCallback(BaseCallback):
    """Backend Callback"""
    def __init__(self):
        super().__init__()
        self.backend = BackendAPI(
            base_url=self.args.API_BASE_ENDPOINT
        )

    def on_step_start(self, state: TaskState, control: TaskControl):
        """Callback for when a step starts."""

    def on_step_end(self, state: TaskState, control: TaskControl):
        """Callback for when a step ends."""
        self.backend.update_task_details(
            task_id=state.task_id,
            status=state.status,
            progress=state.progress
        )

    def on_start(self, state: TaskState, control: TaskControl):
        """Callback for when a task starts."""
        self.backend.update_task_details(
            task_id=state.task_id,
            status=state.status,
            status_desc=state.status_desc,
            progress=state.progress,
            start_time=datetime.datetime.now().isoformat()
        )

    def on_success(self, state: TaskState, control: TaskControl):
        """Callback for when a task is successful."""
        self.backend.set_outputs(
            task_id=state.task_id,
            outputs=state.outputs
        )

        self.backend.update_task_details(
            task_id=state.task_id,
            status=state.status,
            status_desc=state.status_desc,
            progress=state.progress,
            end_time=datetime.datetime.now().isoformat()
        )

    def on_failure(self, state: TaskState, control: TaskControl):
        """Callback for when a task fails."""
        self.backend.update_task_details(
            task_id=state.task_id,
            status=state.status,
            status_desc=state.status_desc,
            progress=state.progress,
            end_time=datetime.datetime.now().isoformat(),
        )

    def on_end(self, state: TaskState, control: TaskControl):
        """Callback for when a task ends."""
