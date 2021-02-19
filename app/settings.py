import time
import logging
import streamlit as st
import pandas as pd
from app.helper_functions import test_watson_connection


def settings_page(state):
    logging.info({"message": "Loading Settings page."})
    st.title(":wrench: Settings")

    if not isinstance(state.watson_args, dict):
        state.watson_args = {"connected": False}

    st.markdown("## Watson Assistant - Credentials")
    st.write(
        "Need help? See this [Finding credentials in the UI](https://cloud.ibm.com/apidocs/assistant/assistant-v2#finding-credentials-in-the-ui) page in the IBM Cloud documentation.")

    if state.watson_args["connected"] == False:
        # Form without default values
        watson_not_connected(state)
    else:
        # Form with default values
        watson_connected(state)


    col1, col2 = st.beta_columns(2)

    # Connect button
    if col1.button("Connect"):
        watson_check = None
        with st.spinner("Connecting"):
            watson_check = test_watson_connection(state.watson_args["skill_id"],
                                                  state.watson_args["apikey"], state.watson_args["endpoint"])
            if isinstance(watson_check, dict):
                if watson_check["status"] == "Not Available":
                    st.error("Fails to connect with Watson Assistant.")
                    state.watson_args["connected"] = False
                    state.watson_args["language"] = watson_check["language"]
                    time.sleep(state.alert_timeout)
                else:
                    st.success("Watson Assistant connected.")
                    state.watson_args["connected"] = True
                    state.watson_args["skill_name"] = watson_check["name"]
                    time.sleep(state.alert_timeout)

    # Disconnect button
    if isinstance(state.watson_args, dict):
        if state.watson_args.get("connected") == True:
            if col2.button("Disconnect"):
                if isinstance(state.watson_args, dict):
                    state.watson_args = None
                    st.success("Watson Assistant has been disconnected.")
                    time.sleep(state.alert_timeout)
                else:
                    st.error("No Watson Assistant skills were connected.")
                    time.sleep(state.alert_timeout)

    st.write("""
    ## NLP - Natural Language Processing
    
    In this session we will configure some NLP features that will be applied to the various analyzes that involve text processing.
    """)

    st.write("""
    ### Stopwords
    Stop words are words which are filtered out before or after processing of natural language data (text).

    You can use "Intents - Stop Words" page to get a list based on your context.
    """)

    uploaded_file = st.file_uploader(
        "Send a list of stopwords", type=["txt"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep="\n", names=["stopwords"])
        if len(df) > 0:
            state.stopwords = df["stopwords"].tolist()
        st.write("Stopwords count: {}".format(len(state.stopwords)))

    state.sync()


def watson_connected(state):
    state.watson_args["skill_id"] = st.text_input(
        "Skill ID", state.watson_args["skill_id"])
    state.watson_args["apikey"] = st.text_input(
        "API key", state.watson_args["apikey"])
    state.watson_args["endpoint"] = st.text_input(
        "Region", state.watson_args["endpoint"])


def watson_not_connected(state):
    state.watson_args["skill_id"] = st.text_input("Skill ID")
    state.watson_args["apikey"] = st.text_input("API key")
    state.watson_args["endpoint"] = st.text_input(
        "Region", "https://api.us-south.assistant.watson.cloud.ibm.com")
