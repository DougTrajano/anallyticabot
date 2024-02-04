"""Docker backend for running tasks."""
import os
import docker
from api.utils.logger import logger
from api.backends.base import BackendBase
from api.backends.factory import BackendFactory
from api.backends.settings import BackendSettings
from worker.tasks.base import TaskBase


class DockerSettings(BackendSettings):
    """Settings for the Docker backend."""

@BackendFactory.register("docker")
class DockerBackend(BackendBase):
    """Docker backend for running tasks."""       

    def run(self, task: TaskBase):
        """Run a task."""
        logger.info("Running task %s with Docker backend.", task.id)

        command = [
            "worker",
            "--task-name",
            task.name,
            "--task-id",
            str(task.id)
        ]
        # test hello world with python image
        # command = ["python", "-c", "print('hello world')"]

        client = docker.from_env()
        container = client.containers.run(
            DockerSettings().WORKER_IMAGE_URI,
            command=command,
            detach=True,
            environment=task.environment,
            mem_limit=task.memory*1024*1024,
            # auto_remove=True,
        )

        logger.info(
            "Task %s is running with Docker backend in container %s.",
            task.id,
            container.id
        )

        return container.id
