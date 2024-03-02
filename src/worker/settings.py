"""Settings for worker service."""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class WorkerSettings(BaseSettings):
    """Settings for worker service."""
    API_BASE_ENDPOINT: Optional[str] = Field(None, description="Base endpoint for API.")
    API_TOKEN: Optional[str] = Field(None, description="API token for authentication.")
