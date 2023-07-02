import requests
from worker.settings import Settings


class Callback(object):
    """Base Callback"""
    def __init__(self):
        self.args = Settings()

    def on_start(self):
        """On Start"""
        pass

    def on_success(self, retval, task_id, args, kwargs):
        """On Success"""
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """On Failure"""
        pass

    def update_task_status(self, task_id, status):
        """Update Task Status"""
        url = '{}/api/v1/task/{}/'.format(self.args.API_ENDPOINT, task_id)
        data = {'status': status}
        requests.patch(url, data=data)