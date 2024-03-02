import streamlit as st
from app.utils.streamlit import streamlit_init

streamlit_init()

def page(title: str = "Stopwords"):
    st.title(title)
    st.sidebar.header(title)
    st.write("""Demo""")
    
if st.session_state.kc.authenticated:
    page()