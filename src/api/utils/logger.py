import logging
from api.utils.settings import Settings

def setup_logger(
        name: str = __file__,
        format: str = Settings().LOGGING_FORMAT,
        level: str = Settings().LOGGING_LEVEL) -> logging.Logger:
    """Function setup as many loggers as you want"""
    formatter = logging.Formatter(format)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

logger = setup_logger()
