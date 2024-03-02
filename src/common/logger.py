"""Module to setup logger for the application."""
import os
import logging

DEFAULT_LOG_FORMAT = "%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s :: %(message)s"

def setup_logger(
        name: str = __file__,
        fmt: str = os.environ.get("LOG_FORMAT", DEFAULT_LOG_FORMAT),
        level: str = os.environ.get("LOG_LEVEL", "INFO"),
        handler: logging.Handler = None) -> logging.Logger:
    """Function setup as many loggers as you want
    
    Args:
    - name: str: Name of the logger.
    - fmt: str: Format of the logger.
    - level: str: Level of the logger.
    - handler: logging.Handler: Handler for the logger.

    Returns:
    - logging.Logger: Logger instance.
    """
    if not handler:
        handler = logging.StreamHandler()

    if fmt:
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)

    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    _logger.addHandler(handler)

    return _logger

logger = setup_logger()
