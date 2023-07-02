import streamlit as st
from utils.init import streamlit_init

streamlit_init()

def page(title: str = "Settings"):
    st.title(title)
    st.sidebar.header(title)
    st.write("""Demo""")
    
if st.session_state.kc.authenticated:
    page()