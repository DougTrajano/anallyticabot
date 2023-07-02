import urllib.parse
import streamlit as st
from utils.settings import Settings

def keycloak_logout_button(
    id_token_hint: str,
    keycloak_url: str = Settings().KEYCLOAK_URL,
    keycloak_realm: str = Settings().KEYCLOAK_REALM,
    keycloak_redirect_uri: str = Settings().KEYCLOAK_REDIRECT_URI
) -> str:
    """Return the logout URL for the Keycloak instance."""
    encoded_redirect_uri = urllib.parse.quote(keycloak_redirect_uri, safe="")

    logout_url = (
        f"{keycloak_url}/realms/{keycloak_realm}/protocol/openid-connect"
        f"/logout?client_id=anallyticabot&post_logout_redirect_uri={encoded_redirect_uri}"
        f"&id_token_hint={id_token_hint}"
    )

    st.sidebar.markdown(
        f"""
        <a href="{logout_url}" target="_self" rel="noopener noreferrer">
        <button type="button" style="background-color: #f63366; color: white;
        border-radius: 5px; padding: 0.5rem 1rem; border: none; font-size: 1rem;
        font-weight: 600; margin-top: 1rem; margin-bottom: 1rem; width: 100%;
        cursor: pointer;">Logout</button></a>
        """,
        unsafe_allow_html=True
    )

    return logout_url
