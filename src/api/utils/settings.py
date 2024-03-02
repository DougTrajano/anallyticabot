import warnings
import uuid
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_DIALECT: str = Field("postgresql+asyncpg", description="Database dialect")
    DATABASE_HOST: str = Field(..., description="Database host")
    DATABASE_PORT: int = Field(..., description="Database port")
    DATABASE_USER: str = Field(..., description="Database user")
    DATABASE_PASSWORD: str = Field(..., description="Database password")
    DATABASE_NAME: str = Field(..., description="Database name")
    DATABASE_DROP_ALL: bool = Field(False, description="Drop all tables on startup")

    # Logging
    LOGGING_LEVEL: str = Field("INFO", description="Logging level")
    LOGGING_FORMAT: str = Field(
        "%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s :: %(message)s",
        description="Logging format"
    )

    # API
    API_TITLE: str = Field("Anallyticabot API", description="API title")
    API_VERSION: str = Field("v1", description="API version")
    API_DESCRIPTION: str = Field(
        "Anallyticabot unlock insights from your data to create the right AI-powered conversational experiences.",
        description="API description"
    )
    API_ROOT_PATH: str = Field("", description="API root path")

class WorkerSettings(BaseSettings):
    WORKER_IMAGE_URI: str = Field(
        "docker.io/dougtrajano/anallyticabot:latest",
        description="The URI of the image to use for the tasks."
    )

    WORKER_BACKEND: str = Field(
        "fargate",
        description="The backend to use for the worker."
    )

    WORKER_API_ENDPOINT: str = Field(
        "http://backend:8000",
        description="API endpoint"
    )

    WORKER_API_TOKEN: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description=(
            "API token used by workers to authenticate with the API. "
            "If not set, it will be generated automatically."
        )
    )

    WORKER_LOG_LEVEL: str = Field(
        "INFO",
        description="Logging level for the worker."
    )

    # send warning when using latest tag
    @validator("WORKER_IMAGE_URI")
    def image_uri_is_latest(cls, v: str): # pylint: disable=no-self-argument, no-self-use
        if v.endswith(":latest"):
            warnings.warn("Using latest tag is not recommended", UserWarning)
        return v
