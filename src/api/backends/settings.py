"""Settings for the backend."""
import uuid
from pydantic import Field
from pydantic_settings import BaseSettings

class BackendSettings(BaseSettings):
    """Settings for the backend."""
    DEBUG: bool = Field(
        default=False,
        description="Whether the backend is running in debug mode."
    )

    WORKER_IMAGE_URI: str = Field(
        default="dougtrajano/anallyticabot:latest",
        description="The URI of the worker image."
    )

    WORKER_API_TOKEN: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="The API token used to authenticate the worker."
    )
