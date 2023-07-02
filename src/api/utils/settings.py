from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    DB_DIALECT: str = Field("postgresql+asyncpg", description="Database dialect")
    DB_HOST: str = Field(..., description="Database host")
    DB_PORT: int = Field(..., description="Database port")
    DB_USER: str = Field(..., description="Database user")
    DB_PASSWORD: str = Field(..., description="Database password")
    DB_NAME: str = Field(..., description="Database name")
    DB_DROP_ALL: bool = Field(False, description="Drop all tables on startup")

    # Logging
    LOGGING_LEVEL: str = Field("DEBUG", description="Logging level")
    LOGGING_FORMAT: str = Field(
        "%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s :: %(message)s",
        description="Logging format"
    )

    # API
    API_TITLE: str = Field("Anallyticabot API", description="API title")
    API_DESCRIPTION: str = Field(
        "Anallyticabot unlock insights from your data to create the right AI-powered conversational experiences.",
        description="API description"
    )
    API_VERSION: str = Field("v1", description="API version")