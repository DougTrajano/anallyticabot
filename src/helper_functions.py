import streamlit as st
import json


def load_parameters(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data


def disable_menu():
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>

    """

    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
