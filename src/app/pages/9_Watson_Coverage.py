"""Watson Coverage Page"""
import asyncio
import requests
import pandas as pd
import streamlit as st
from utils.streamlit import app_init
from utils.settings import args

app_init()

st.title("Watson Coverage")
st.write(
    """
    In this page, we can check the coverage of examples in the Watson Assistant.

    The coverage is calculated as the number of examples that are covered 
    by the Watson Assistant with a confidence above a given threshold.
    
    It is useful to check if a new intent could cause a conflict with the existing ones.
    """
)

if "task_id" in st.session_state:
    st.write(f"Task ID: {st.session_state.task_id}")

st.header("Upload Data")
st.write("Upload a CSV/JSON file with the examples to check the coverage.")
file = st.file_uploader("Upload file", type=["csv", "json"])

with st.expander("Advanced Options"):
    st.write("Select the parameters for the Watson Assistant.")
    watson_apikey = st.text_input(
        "Watson API Key",
        type="password",
        help="The API Key for the Watson Assistant."
    )

    watson_url = st.text_input(
        "Watson URL",
        value='https://api.us-south.assistant.watson.cloud.ibm.com',
        help="The URL for the Watson Assistant."
    )

    watson_version = st.text_input(
        "Watson Version",
        value='2023-06-15',
        help="The version for the Watson Assistant."
    )

    watson_assistant_id = st.text_input(
        "Watson Assistant ID",
        help="The ID for the Watson Assistant."
    )

    watson_user_id = st.text_input(
        "Watson User ID",
        value="anallyticabot",
        help="The User ID for the Watson Assistant."
    )

    watson_alternate_intents = st.checkbox(
        "Watson Alternate Intents",
        value=False,
        help="Whether to return more than one intent."
    )

    threshold = st.slider(
        "Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.01,
        help="The threshold for the Watson Assistant confidence."
    )

if file is not None:
    if file.name.endswith(".csv"):
        data = pd.read_csv(file)
    elif file.name.endswith(".json"):
        data = pd.read_json(file)

    # st. columns
    c1, _ = st.columns(2)

    example_column = c1.selectbox("Select the column with the examples.", data.columns)
    if st.button("Create task"):
        response = requests.post(
            url=f"{args.API_INTERNAL_URL}/tasks",
            timeout=60,
            json={
                "name": "watson_coverage",
                "created_by": "anallyticabot",
                "inputs": {
                    "data": data.to_dict(orient="records")
                },
                "params": {
                    "threshold": threshold,
                    "watson_apikey": watson_apikey,
                    "watson_url": watson_url,
                    "watson_version": watson_version,
                    "watson_assistant_id": watson_assistant_id,
                    "watson_user_id": watson_user_id,
                    "watson_alternate_intents": watson_alternate_intents,
                    "watson_example_column": example_column
                }
            }
        )

        if response.status_code in [200, 201]:
            res = response.json()
            st.session_state.task_id = res["task_id"]
            st.toast(res.get("message", "Task created successfully."), icon="✅")
            st.write("You can check the status of the task in the [Tasks](/Tasks) page.")
            asyncio.sleep(5)
            st.rerun()
        else:
            st.toast(f"Error creating task: {response.text}", icon="❌")
