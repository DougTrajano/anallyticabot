import streamlit as st
from app.helper_functions import *
from io import StringIO
import numpy as np
import pandas as pd
import time

def settings_page(state):

    st.title(":wrench: Settings")

    if not isinstance(state.watson_args, dict):
        state.watson_args = {"connected": False}

    st.markdown("## Watson Assistant - Credenciais")
    st.write(
        "Precisa de ajuda? Veja essa página [Finding credentials in the UI](https://cloud.ibm.com/apidocs/assistant/assistant-v2#finding-credentials-in-the-ui) na documentação da IBM Cloud.")

    st.write(state.watson_args)

    if state.watson_args["connected"] == False:
        # Form without default values
        watson_not_connected(state)
    else:
        # Form with default values
        watson_connected(state)

    # Connect button
    connect_button(state)

    # Desconnect button
    if isinstance(state.watson_args, dict):
        if state.watson_args.get("connected") == True:
            desconnect_button(state)

    st.write("""
    ## NLP
    
    Nessa sessão nós vamos configurar o que será aplicado nas diversas análises que envolvem processamento de texto.
    """)

    uploaded_file = st.file_uploader(
        "Stopwords: (stopwords.txt)", type=["txt"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep="\n", names=["stopwords"])
        if len(df) > 0:
            state.stopwords = df["stopwords"].tolist()
        st.write("Stopwords uploaded: {}".format(len(state.stopwords)))
    
    #state.sync()


def watson_connected(state):
    state.watson_args["skill_name"] = st.text_input(
        "Chatbot name", state.watson_args["skill_name"])
    state.watson_args["skill_id"] = st.text_input(
        "Skill ID", state.watson_args["skill_id"])
    state.watson_args["apikey"] = st.text_input(
        "API key", state.watson_args["apikey"])
    state.watson_args["endpoint"] = st.text_input(
        "Region", state.watson_args["endpoint"])


def watson_not_connected(state):
    state.watson_args["skill_name"] = st.text_input("Chatbot name")
    state.watson_args["skill_id"] = st.text_input("Skill ID")
    state.watson_args["apikey"] = st.text_input("API key")
    state.watson_args["endpoint"] = st.text_input(
        "Region", "https://api.us-south.assistant.watson.cloud.ibm.com")


def connect_button(state):
    watson_check = None
    if st.button("Conectar"):
        watson_check = test_watson_connection(
            state.watson_args["skill_id"], state.watson_args["apikey"], state.watson_args["endpoint"])
        if isinstance(watson_check, dict):
            if watson_check["status"] == "Not Available":
                st.error("Falha ao tentar conectar com o Watson Assistant.")
                state.watson_args["connected"] = False
                time.sleep(0.5)
            else:
                st.info("Watson Assistant conectado com sucesso.")
                state.watson_args["connected"] = True
                time.sleep(0.5)

def desconnect_button(state):
    if st.button("Desconectar"):
        if isinstance(state.watson_args, dict):
            state.watson_args = None
            st.success("Watson Assistant foi desconectado.")
            time.sleep(0.5)
        else:
            st.error("Nenhuma skill do Watson Assistant estava conectada.")
            time.sleep(0.5)
