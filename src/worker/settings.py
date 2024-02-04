"""Settings for worker service."""	
from pydantic_settings import BaseSettings
from pydantic import Field

class WorkerSettings(BaseSettings):
    """Settings for worker service."""
    API_BASE_ENDPOINT: str = Field(..., description="Base endpoint for API.")
    API_TOKEN: str = Field(..., description="API token for authentication.")
