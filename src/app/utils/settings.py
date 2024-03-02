"""Settings for the app."""	
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the app."""
    ALERT_TIMEOUT: float = 0.3

    STREAMLIT_TITLE: str = "Anallyticabot"
    STREAMLIT_LAYOUT: str = "wide"
    STREAMLIT_ICON: str = "images/icon.ico"
    STREAMLIT_DISABLE_MENU: bool = True

    API_INTERNAL_URL: str = "http://backend:8000"
    API_EXTERNAL_URL: str = "http://localhost:8000"
    API_TIMEOUT: int = 120

args = Settings()
