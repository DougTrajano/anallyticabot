import streamlit as st

def main_page(state):
    no_chatbot_connected(state)

def no_chatbot_connected(state):
    st.title("Anallyticabot")
    st.write("""
    Anallyticabot é uma plataforma que fornece **advanced analytics** para ajudar você a melhorar seu chatbot.
    
    Aqui você poderá analisar intenções, entidades, diálogos e muito mais.
    """)
    
    st.write("""
    ## Como começar?

    - Vá até a página "Settings" e conecte com seu Watson Assistant skill.
    - Ainda em "Settings", você poderá definir as configurações globais da plataforma.
    """)

    st.write("""
    ## Recursos

    ### Intenções (intents)

    Pendente
    
    ### Entidades (entities)

    Pendente

    ### Diálogos (dialogs)

    Pendente
    """)