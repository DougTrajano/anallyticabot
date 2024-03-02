"""Example Task"""
from worker.tasks.base import TaskBase
from worker.tasks.factory import TaskFactory


@TaskFactory.register("example")
class ExampleTask(TaskBase):
    """Example Task"""
    _name: str = "example"
    _version: str = "1.0"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self, **kwargs) -> None:
        """Run Task"""
        print("Hello World!")
        