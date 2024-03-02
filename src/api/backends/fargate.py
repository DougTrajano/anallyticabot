"""A backend for running tasks on AWS Fargate."""
import time
from typing import Any, Dict, List, Optional

import boto3
from pydantic import Field
from api.backends.base import BackendBase
from api.backends.factory import BackendFactory
from api.backends.settings import BackendSettings
from common.logger import logger
from worker.tasks.base import TaskBase


class FargateSettings(BackendSettings):
    """Settings for the AWS Fargate backend."""	
    FARGATE_CLUSTER_NAME: str = Field(
        "anallyticabot", description="The name of the cluster to create."
    )

    FARGATE_CLUSTER_TAGS: Optional[Dict[str, str]] = Field(
        None, description="The tags to apply to the cluster."
    )

    FARGATE_SUBNET_IDS: List[str] = Field(
        None, description="The IDs of the subnets to use for the cluster."
    )

    FARGATE_SECURITY_GROUP_IDS: List[str] = Field(
        None, description="The IDs of the security groups to use for the cluster."
    )

    FARGATE_DEFAULT_NAMESPACE: str = Field(
        "anallyticabot", description="The default namespace to use for the cluster."
    )

    FARGATE_CONTAINER_INSIGHTS: bool = Field(
        True, description="Enable container insights for the cluster."
    )

    FARGATE_TASK_ROLE_ARN: str = Field(
        None, description="The ARN of the IAM role to use for the tasks."
    )

    FARGATE_EXECUTION_ROLE_ARN: str = Field(
        None, description="The ARN of the IAM role to use for the execution role."
    )

    FARGATE_TASK_TAGS: Optional[Dict[str, str]] = Field(
        None, description="The tags to apply to the tasks."
    )

    FARGATE_NETWORK_MODE: str = Field(
        "awsvpc", description="The network mode to use for the tasks."
    )

    FARGATE_PORT_MAPPING: List[Dict[str, Any]] = Field(
        [{"containerPort": 80, "hostPort": 80, "protocol": "tcp"}],
        description="The port mapping to use for the tasks."
    )

@BackendFactory.register("fargate")
class FargateBackend(BackendBase):
    """A backend for running tasks on AWS Fargate."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aws_region = boto3.Session().region_name
        self.client = boto3.client("ecs", region_name=self.aws_region)
        self.args = FargateSettings()

        if not self.get_cluster_info(self.args.FARGATE_CLUSTER_NAME)["clusters"]:
            logger.info("ECS cluster %s not found. Creating...", self.args.FARGATE_CLUSTER_NAME)
            self.create_cluster(
                cluster_name=self.args.FARGATE_CLUSTER_NAME,
                cluster_namespace=self.args.FARGATE_DEFAULT_NAMESPACE,
                cluster_tags=self.args.FARGATE_CLUSTER_TAGS,
                container_insights=self.args.FARGATE_CONTAINER_INSIGHTS,
                wait_for_cluster_creation=True
            )

    def run(self, task: TaskBase):
        """Run the given task on AWS Fargate.

        Args:
        - task (Task): The task to run.

        Returns:
        - dict: The response from the run_task call.
        """
        logger.info("Running task %s on AWS Fargate.", task.name)

        command = [
            "worker",
            "--task-name",
            task.name,
            "--task-id",
            str(task.id)
        ]

        if not self.check_task_definition_exists(
            task_definition_name=task.name,
            image_uri=self.args.WORKER_IMAGE_URI,
            cpu=task.cpu,
            memory=task.memory_in_mb,
            task_tags=self.args.FARGATE_TASK_TAGS):

            logger.info("Task definition %s not found. Creating...", task.name)

            self.create_task_definition(
                task_definition_name=task.name,
                image_uri=self.args.WORKER_IMAGE_URI,
                cpu=task.cpu,
                memory=task.memory_in_mb,
                task_role_arn=self.args.FARGATE_TASK_ROLE_ARN,
                execution_role_arn=self.args.FARGATE_EXECUTION_ROLE_ARN,
                task_tags=self.args.FARGATE_TASK_TAGS
            )

        response = self.run_task(
            task_definition_name=task.name,
            cluster_name=self.args.FARGATE_CLUSTER_NAME,
            subnet_ids=self.args.FARGATE_SUBNET_IDS,
            security_group_ids=self.args.FARGATE_SECURITY_GROUP_IDS,
            assign_public_ip=True,
            command=command,
            environment=task.environment,
            cpu=task.cpu,
            memory=task.memory_in_mb
        )

        return response

    def create_cluster(
            self,
            cluster_name: str = None,
            cluster_namespace: str = None,
            cluster_tags: Dict[str, str] = None,
            container_insights: bool = None,
            wait_for_cluster_creation: bool = True):
        """Create a cluster with the given name.
        
        Args:
        - cluster_name (str): The name of the cluster to create.
        - cluster_namespace (str): The namespace to use for the cluster.
        - cluster_tags (dict): The tags to apply to the cluster.
        - container_insights (bool): Whether to enable container insights for the cluster.
        - wait_for_cluster_creation (bool): Whether to wait for the cluster to be created.
        
        Returns:
        - dict: The response from the create_cluster call.
        """
        if not cluster_name:
            cluster_name = self.args.FARGATE_CLUSTER_NAME
        if not cluster_namespace:
            cluster_namespace = self.args.FARGATE_DEFAULT_NAMESPACE
        if not cluster_tags:
            cluster_tags = self.args.FARGATE_CLUSTER_TAGS
        if not container_insights:
            container_insights = self.args.FARGATE_CONTAINER_INSIGHTS

        logger.debug("Creating cluster %s.", cluster_name)

        response = self.client.create_cluster(
            clusterName=cluster_name,
            tags=cluster_tags if cluster_tags else [],
            capacityProviders=[
                "FARGATE",
                "FARGATE_SPOT"
            ],
            settings=[
                {
                    "name": "containerInsights",
                    "value": "enabled"
                },
            ] if container_insights else [],
            serviceConnectDefaults={
                "namespace": cluster_namespace
            }
        )

        logger.debug("Response: %s", response)

        if wait_for_cluster_creation:
            while True:
                response = self.get_cluster_info(cluster_name)
                if response["clusters"][0]["status"] == "ACTIVE":
                    break
                logger.debug("Waiting for cluster %s to be created.", cluster_name)
                time.sleep(2)

        return response

    def get_cluster_info(self, cluster_name: str, include: List[str] = None):
        """Get the cluster info for the given cluster name.
        
        Args:
        - cluster_name (str): The name of the cluster to get info for.
        - include (list): The info to include in the response (as boto3 expects).
        
        Returns:
        - dict: The response from the describe_clusters call.
        """
        logger.debug("Getting cluster info for cluster %s.", cluster_name)

        response = self.client.describe_clusters(
            clusters=[
                cluster_name,
            ],
            include=include if include else [],
        )

        logger.debug("Response: %s", response)

        return response

    def validate_fargate_specs(self, cpu: int, memory: int):
        """Validate the given CPU and memory values against the Fargate specs.

        Args:
        - cpu (int): The number of CPU units to reserve for the container.
        - memory (int): The amount (in MiB) of memory to present to the container.

        Returns:
        - bool: Whether the CPU and memory values are valid.
        """
        cpu_memory_specs = {
            256: [512, 1024, 2048],
            512: [1024, 2048, 3072, 4096],
            1024: [2048, 3072, 4096, 5120, 6144, 7168, 8192],
            2048: range(4096, 16384 + 1, 1024),
            4096: range(8192, 30720 + 1, 1024),
            8192: range(16384, 61440 + 1, 1024),
            16384: range(32768, 120000 + 1, 1024)
        }

        if cpu not in cpu_memory_specs:
            raise ValueError(f"Invalid CPU value: {cpu}")

        if memory not in cpu_memory_specs[cpu]:
            raise ValueError(f"Invalid memory value: {memory}")

        return True

    def check_task_definition_exists(
            self,
            task_definition_name: str,
            image_uri: str,
            cpu: int = 256,
            memory: int = 512,
            port_mappings: List[Dict[str, int]] = None,
            network_mode: str = None,
            task_role_arn: str = None,
            execution_role_arn: str = None,
            secrets: List[Dict[str, str]] = None,
            task_tags: Dict[str, str] = None):
        """Check if a task definition with the given name exists.

        Args:
        - task_definition_name (str): The name of the task definition to check.
        - image_uri (str): The URI of the image to use for the task definition.
        - cpu (int): The number of CPU units to reserve for the container.
        - memory (int): The amount (in MiB) of memory to present to the container.
        - port_mappings (list): The port mappings to use for the container.
        - network_mode (str): The network mode to use for the container.
        - task_role_arn (str): The ARN of the IAM role to use for the task.
        - execution_role_arn (str): The ARN of the IAM role to use for the execution role.
        - secrets (list): The secrets to use for the container.
        - task_tags (dict): The tags to apply to the task.

        Returns:
        - bool: Whether the task definition exists.
        """
        if not port_mappings:
            port_mappings = FargateSettings().FARGATE_PORT_MAPPING
        if not network_mode:
            network_mode = FargateSettings().FARGATE_NETWORK_MODE
        if not task_role_arn:
            task_role_arn = FargateSettings().FARGATE_TASK_ROLE_ARN
        if not execution_role_arn:
            execution_role_arn = FargateSettings().FARGATE_EXECUTION_ROLE_ARN
        if not task_tags:
            task_tags = FargateSettings().FARGATE_TASK_TAGS

        logger.debug("Checking if task definition %s exists.", task_definition_name)

        secrets = secrets if secrets else []

        try:
            response = self.client.describe_task_definition(
                taskDefinition=task_definition_name,
                include=["TAGS"]
            )
            logger.debug("Response: %s", response)

            task = response["taskDefinition"]
            if task["containerDefinitions"][0]["image"] != image_uri:
                logger.debug(
                    "Task definition %s exists but image URI does not match. "
                    "Expected: %s, Actual: %s",
                    task_definition_name, image_uri,
                    task["containerDefinitions"][0]["image"]
                )
                return False
            elif task["containerDefinitions"][0]["secrets"] != secrets:
                logger.debug(
                    "Task definition %s exists but secrets do not match. "
                    "Expected: %s, Actual: %s",
                    task_definition_name, secrets,
                    task["containerDefinitions"][0]["secrets"]
                )
                return False
            elif task["containerDefinitions"][0]["portMappings"] != port_mappings:
                logger.debug(
                    "Task definition %s exists but port mappings do not match. "
                    "Expected: %s, Actual: %s",
                    task_definition_name, port_mappings,
                    task["containerDefinitions"][0]["portMappings"]
                )
                return False
            elif task["cpu"] != str(cpu):
                logger.debug(
                    "Task definition %s exists but CPU does not match. "
                    "Expected: %s, Actual: %s",
                    task_definition_name, cpu, task["cpu"]
                )
                return False
            elif task["memory"] != str(memory):
                logger.debug(
                    "Task definition %s exists but memory does not match. "
                    "Expected: %s, Actual: %s",
                    task_definition_name, memory, task["memory"]
                )
                return False
            elif task["networkMode"] != network_mode:
                logger.debug(
                    "Task definition %s exists but network mode does not match. "
                    "Expected: %s, Actual: %s",
                    task_definition_name, network_mode, task["networkMode"]
                )
                return False
            elif task["taskRoleArn"] != task_role_arn:
                logger.debug(
                    "Task definition %s exists but task role ARN does not match. "
                    "Expected: %s, Actual: %s",
                    task_definition_name, task_role_arn, task["taskRoleArn"]
                )
                return False
            elif task["executionRoleArn"] != execution_role_arn:
                logger.debug(
                    "Task definition %s exists but execution role ARN does not match. "
                    "Expected: %s, Actual: %s",
                    task_definition_name, execution_role_arn, task["executionRoleArn"]
                )
                return False
            # TODO: TECH DEBT Check tags
            # elif response["tags"] != [{"key": k, "value": v} for k, v in task_tags.items()]:
            #     logger.debug(
            #         f"Task definition {task_definition_name} exists but tags do not match. "
            #         f"Expected: {task_tags}, Actual: {task['tags']}"
            #     )
            #     return False
            else:
                logger.debug("Task definition %s exists.", task_definition_name)
                return True
        except self.client.exceptions.ClientException as ecs_exception:
            logger.debug(
                "Task definition %s does not exist. Exception: %s",
                task_definition_name, ecs_exception
            )
            return False

    def create_task_definition(
            self,
            task_definition_name: str,
            image_uri: str,
            cpu: int = 256,
            memory: int = 512,
            port_mappings: List[Dict[str, int]] = None,
            network_mode: str = None,
            task_role_arn: str = None,
            execution_role_arn: str = None,
            command: List[str] = None,
            environment: Dict[str, str] = None,
            secrets: List[Dict[str, str]] = None,
            task_tags: Dict[str, str] = None):
        """Create a task definition with the given name.

        Args:
        - task_definition_name (str): The name of the task definition to create.
        - image_uri (str): The URI of the image to use for the task definition.
        - cpu (int): The number of CPU units to reserve for the container.
        - memory (int): The amount (in MiB) of memory to present to the container.
        - port_mappings (list): The port mappings to use for the container.
        - network_mode (str): The network mode to use for the container.
        - task_role_arn (str): The ARN of the IAM role to use for the task.
        - execution_role_arn (str): The ARN of the IAM role to use for the execution role.
        - command (list): The command to use for the container.
        - environment (dict): The environment variables to use for the container.
        - secrets (list): The secrets to use for the container.
        - task_tags (dict): The tags to apply to the task.

        Returns:
        - dict: The response from the register_task_definition call.
        """
        if not port_mappings:
            port_mappings = FargateSettings().FARGATE_PORT_MAPPING
        if not network_mode:
            network_mode = FargateSettings().FARGATE_NETWORK_MODE
        if not task_role_arn:
            task_role_arn = FargateSettings().FARGATE_TASK_ROLE_ARN
        if not execution_role_arn:
            execution_role_arn = FargateSettings().FARGATE_EXECUTION_ROLE_ARN
        if not task_tags:
            task_tags = FargateSettings().FARGATE_TASK_TAGS

        self.validate_fargate_specs(cpu, memory)

        logger.debug("Creating task definition %s.", task_definition_name)

        response = self.client.register_task_definition(
            family=task_definition_name,
            taskRoleArn=task_role_arn,
            executionRoleArn=execution_role_arn,
            networkMode=network_mode,
            requiresCompatibilities=["FARGATE"],
            cpu=str(cpu),
            memory=str(memory),
            tags=[
                {
                    "key": k,
                    "value": v
                } for k, v in task_tags.items()
            ],
            containerDefinitions=[
                {
                    "name": task_definition_name,
                    "image": image_uri,
                    "cpu": cpu,
                    "memory": memory,
                    "essential": True,
                    "portMappings": port_mappings,
                    "command": command if command else [],
                    "environment": [
                        {
                            "name": k,
                            "value": v
                        } for k, v in environment.items()
                    ] if environment else [],
                    "secrets": secrets if secrets else [],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-create-group": "true",
                            "awslogs-group": task_definition_name,
                            "awslogs-region": self.aws_region,
                            "awslogs-stream-prefix": task_definition_name
                        }
                    }
                },
            ]
        )

        logger.debug("Response: %s", response)

        return response

    def run_task(
            self,
            task_definition_name: str,
            task_count: int = 1,
            cluster_name: str = None,
            launch_type: str = "FARGATE",
            platform_version: str = "LATEST",
            subnet_ids: List[str] = None,
            security_group_ids: List[str] = None,
            assign_public_ip: bool = False,
            command: List[str] = None,
            environment: Dict[str, str] = None,
            cpu: int = 256,
            memory: int = 512,
            storage_in_gb: int = 21):
        """Run a task with the given name.

        Args:
        - task_definition_name (str): The name of the task definition to use.
        - task_count (int): The number of tasks to run.
        - cluster_name (str): The name of the cluster to run the task on.
        - launch_type (str): The launch type to use for the task.
        - platform_version (str): The platform version to use for the task.
        - subnet_ids (list): The IDs of the subnets to use for the task.
        - security_group_ids (list): The IDs of the security groups to use for the task.
        - assign_public_ip (bool): Whether to assign a public IP to the task.
        - command (list): The command to use for the container.
        - environment (dict): The environment variables to use for the container.
        - cpu (int): The number of CPU units to reserve for the container.
        - memory (int): The amount (in MiB) of memory to present to the container.
        - storage_in_gb (int): The amount (in GiB) of ephemeral storage to present to the container.        

        Returns:
        - dict: The response from the run_task call.
        """
        if not cluster_name:
            cluster_name = self.args.FARGATE_CLUSTER_NAME
        if not subnet_ids:
            subnet_ids = self.args.FARGATE_SUBNET_IDS

        self.validate_fargate_specs(cpu, memory)

        logger.debug("Running task %s on cluster %s.", task_definition_name, cluster_name)

        response = self.client.run_task(
            cluster=cluster_name,
            taskDefinition=task_definition_name,
            count=task_count,
            launchType=launch_type,
            platformVersion=platform_version,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "securityGroups": security_group_ids if security_group_ids else [],
                    "assignPublicIp": "ENABLED" if assign_public_ip else "DISABLED"
                }
            },
            overrides={
                "containerOverrides": [
                    {
                        "name": task_definition_name,
                        "command": command if command else [],
                        "environment": [
                            {
                                "name": k,
                                "value": v
                            } for k, v in environment.items()
                        ] if environment else [],
                        "cpu": cpu,
                        "memory": memory
                    },
                ],
                "cpu": str(cpu),
                "memory": str(memory),
                "ephemeralStorage": {
                    "sizeInGiB": storage_in_gb
                }
            },
        )

        logger.debug("Response: %s", response)

        return response
    