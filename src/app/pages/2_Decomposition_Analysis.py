import streamlit as st
from utils.streamlit import app_init

app_init()

def page(title: str = "Decomposition Analysis"):
    st.title(title)
    st.write("""Demo""")
    
page()