"""Watson Coverage Task."""
from worker.tasks.base import TaskBase
from worker.tasks.factory import TaskFactory


@TaskFactory.register("watson_coverage")
class WatsonCoverage(TaskBase):
    """Watson Coverage Task."""
    _name: str = "watson_coverage"
    _version: str = "1.0"

    def run(self, **kwargs) -> None:
        """Run Task"""
        print("Hello World!")
