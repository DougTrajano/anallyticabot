import logging

def setup_logger():
    # Define formatter
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s :: %(message)s')

    # Define handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Create logger instance
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)

    # Set logging level
    logger.setLevel(logging.INFO)
    
    return logger