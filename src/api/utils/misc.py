import uuid

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
