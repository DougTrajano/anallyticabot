import streamlit as st
from utils.init import streamlit_init

streamlit_init()

def main(title: str = "Anallyticabot"):
    st.title(title)
    st.subheader(f"Welcome {st.session_state.kc.user_info['preferred_username']}!")
    st.write(f"Here is your user information:")
    st.write(st.session_state.kc)

if st.session_state.kc.authenticated:
    main()