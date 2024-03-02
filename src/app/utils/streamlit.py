"""Streamlit utility functions"""
import streamlit as st
from streamlit.logger import get_logger
from utils.plotly import setup_plotly_theme
from utils.settings import settings

_logger = get_logger('root')
_logger.info("Anallyticabot started.")

def disable_st_menu():
    """Disables the Streamlit menu"""
    hide_streamlit_style = """
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
    """

    st.markdown(
        hide_streamlit_style,
        unsafe_allow_html=True
    )

def app_init():
    """Initializes the Streamlit app with the settings from the settings file"""
    st.set_page_config(
        page_title=settings.STREAMLIT_TITLE,
        page_icon=settings.STREAMLIT_ICON,
        layout=settings.STREAMLIT_LAYOUT
    )

    disable_st_menu()
    setup_plotly_theme()
