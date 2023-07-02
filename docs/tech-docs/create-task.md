# Create Task

First, you need to know that we have two types of tasks: **async** and **sync**. The first one is used when you need to run a task that will take a long time to finish, and the second one is used when you need to run a task that will take a short time to finish.

## Async

1. Create a new file under the `src.worker.tasks` folder.

2. Develop a new class that inherits from `src.worker.tasks.base.Task` and implement the `run` method. This method will be called when the task is executed.

3. You also need to add the `src.worker.tasks.factory.TaskFactory.register` decorator to the class. This decorator will register the task in the task factory.

```python
from src.worker.tasks.base import Task
from src.worker.tasks.factory import TaskFactory


@TaskFactory.register("example")
class ExampleTask(Task):
    """Example Task"""
    _version = "1.0"

    def run(self, **kwargs) -> None:
        """Run Task"""
        print("Hello World!")
```

The `_version` attribute is used to identify the task version in the database. If you don't specify the version, the default value will be `1.0`. You can increment the version when you need to change the task code. It's useful to identify which version of the task was executed.

## Sync

Sync tasks are short-lived executions that can be done inside the API.

Pending
