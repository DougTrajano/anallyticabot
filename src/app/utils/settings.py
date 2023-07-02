from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    ALERT_TIMEOUT: float = 0.3

    KEYCLOAK_URL: str = "http://localhost:3333/"
    KEYCLOAK_REALM: str = "master"
    KEYCLOAK_CLIENT_ID: str = "anallyticabot"
    KEYCLOAK_REDIRECT_URI: str = "http://localhost:8501/#"

    STREAMLIT_TITLE: str = "Anallyticabot"
    STREAMLIT_LAYOUT: str = "wide"
    STREAMLIT_ICON: str = "images/icon.ico"
    STREAMLIT_DISABLE_MENU: bool = False