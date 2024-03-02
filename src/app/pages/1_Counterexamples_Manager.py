"""A page for managing IBM Watsonx Assistant counterexamples."""
import streamlit as st
from utils.streamlit import app_init

app_init()

def page():
    """Counterexamples Manager page."""
    st.title("Counterexamples Manager")
    st.write("Demo")

page()
