from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    
    API_ENDPOINT: str = Field("http://localhost:8000", description="API endpoint")
    # API_TOKEN: str = Field(..., description="API token")

    