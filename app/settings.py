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

    # Watson Credentials
    st.markdown("## Watson Assistant - Credentials")
    st.write(
        "Need help? See this [Finding credentials in the UI](https://cloud.ibm.com/apidocs/assistant/assistant-v2#finding-credentials-in-the-ui) page in the IBM Cloud documentation.")

    with st.form(key="Watson Credentials"):
        default_values = {}
        if state.watson_args["connected"] == False:
            default_values["skill_id"] = ""
            default_values["apikey"] = ""
            default_values["endpoint"] = "https://api.us-south.assistant.watson.cloud.ibm.com"
        else:
            default_values["skill_id"] = state.watson_args["skill_id"]
            default_values["apikey"] = state.watson_args["apikey"]
            default_values["endpoint"] = state.watson_args["endpoint"]

        state.watson_args["skill_id"] = st.text_input(label="Skill ID",
                                                      value=default_values["skill_id"])

        state.watson_args["apikey"] = st.text_input(label="API Key",
                                                    value=default_values["apikey"],
                                                    type="password")

        state.watson_args["endpoint"] = st.text_input(label="Region",
                                                      value=default_values["endpoint"])

        connect_button = st.form_submit_button("Connect")

    if connect_button:
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

    # OpenAI GPT-3 Credentials
    if not isinstance(state.openai, dict):
        state.openai = {}

    st.write("## OpenAI GPT-3")
    st.markdown("GPT-3 is an autoregressive language model that uses deep learning to produce human-like text. We use GPT-3 in utterance generator.")

    state.openai["apikey"] = st.text_input(label="API Key", key="openai_key",
                                           value="" if state.openai.get("apikey") in [None, ""] else state.openai.get("apikey"),
                                           type="password",
                                           help="Get your API key in [beta.openai.com/account/api-keys](https://beta.openai.com/account/api-keys)")

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
