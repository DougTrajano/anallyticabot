from utils.logger import logger

class Kubernetes(object):
    def __init__(self) -> None:
        pass

    def run_task(self, task_definition, namespace, overrides):
        pass

    def stop_task(self, task_id, namespace):
        pass

    def get_status(self, task_id, namespace):
        pass