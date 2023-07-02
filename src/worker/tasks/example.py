from worker.tasks.base import Task
from worker.tasks.factory import TaskFactory


@TaskFactory.register("example")
class ExampleTask(Task):
    """Example Task"""
    _version = "1.0"

    def run(self, **kwargs) -> None:
        """Run Task"""
        print("Hello World!")
        