import streamlit as st
# from streamlit_keycloak import login
from utils.logger import setup_logger
from utils.plotly import setup_plotly_theme
from utils.auth import keycloak_logout_button
from utils.settings import Settings

args = Settings()

logger = setup_logger()
logger.info("Anallyticabot started.")

def disable_st_menu():
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def streamlit_init():    
    st.set_page_config(
        page_title=args.STREAMLIT_TITLE,
        page_icon=args.STREAMLIT_ICON,
        layout=args.STREAMLIT_LAYOUT
    )

    disable_st_menu()
    setup_plotly_theme()

    # st.session_state.kc = login(
    #     url=args.KEYCLOAK_URL,
    #     realm=args.KEYCLOAK_REALM,
    #     client_id=args.KEYCLOAK_CLIENT_ID
    # )

    st.session_state.kc.authenticated = True
    # if st.session_state.kc.authenticated:
    #     keycloak_logout_button(id_token_hint=st.session_state.kc.id_token)
