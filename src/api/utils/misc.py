import uuid
from worker.tasks.factory import TaskFactory

def is_valid_uuid(value: str):
    """Check if value is a valid UUID

    Args:
    - value (str): Value to check.

    Returns:
    - bool: True if value is a valid UUID, False otherwise.
    """
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False

def check_task_exists(task_name: str):
    """Check if task exists.

    Args:
    - task_name (str): Task name to check.

    Returns:
    - bool: True if task exists, False otherwise.
    """
    if task_name not in TaskFactory.registry.keys():
        return False
    return True