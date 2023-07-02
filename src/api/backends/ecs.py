from utils.logger import logger

class ECS(object):
    def __init__(self):
        """ECS Task Runner"""
        pass

    def get_task_definition(self, task_definition):
        pass

    def run_task(self, task_definition, cluster, overrides):
        pass

    def stop_task(self, task_id, cluster):
        pass

    def get_status(self, task_id, cluster):
        pass