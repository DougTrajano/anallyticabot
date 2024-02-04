from worker.tasks.base import TaskBase


class TaskFactory:
    """The factory class for creating tasks."""
    registry = {}

    @classmethod
    def register(cls, name: str) -> callable:
        """Registers a task class in the factory.

        Args:
        - name (str): The name of the task.

        Returns:
        - callable: A decorator.
        """
        def decorator(task_cls: TaskBase) -> TaskBase:
            cls.registry[name] = task_cls
            return task_cls
        return decorator
    
    @classmethod
    def create_executor(cls, task_id: str, task_name: str) -> TaskBase:
        """Creates a task executor.

        Args:
        - task_id (str): The task id.
        - task_name (str): The task name.

        Returns:
        - Task: A task executor.
        """        
        task_cls = cls.registry.get(task_name)
        if task_cls is None:
            raise Exception(f"Task {task_name} not found. Registry: {cls.registry}")
        return task_cls(task_id=task_id)
