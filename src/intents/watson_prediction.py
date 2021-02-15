import streamlit as st
import pandas as pd
import logging
from src.connectors.watson_assistant import WatsonAssistant


def eval_intent_col(df):
    """
    Check values for intent column. If doesn't exists, drop de column.
    """
    if "intent" in df.columns:
        if df["intents"].notnull().sum() == 0:
            df.drop(columns=["intents"], errors="ignore", inplace=True)
    return df


@st.cache
def cache_df(df):
    return df


def run_wa_preds(df, watson_apikey, watson_endpoint, watson_skill):
    """
    Get Watson Assistant predictions for the first 3 intents with a single call at time.

    Arguments:
    - df (pd.DataFrame, required): data with "examples" columns.
    - watson_apikey (str, required): Watson apikey used on WatsonAssistant class.
    - watson_endpoint (str, required): Watson endpoint used on WatsonAssistant class.
    - watson_skill (str, required): Watson skill used on WatsonAssistant class.

    Output:
    DataFrame with the same df's columns and more ...
    """

    logging.info({"message": "Applying Watson Assistant predictings."})

    wa = WatsonAssistant(apikey=watson_apikey,
                         service_endpoint=watson_endpoint,
                         default_skill_id=watson_skill)
    new_df = []

    counter = 0
    pbar = st.progress(counter)

    for row in df.to_dict(orient="records"):
        processed_row = send_message(row, "examples", wa)
        new_df.append(processed_row)
        counter += 1
        pbar.progress(counter / len(df))

    new_df = pd.DataFrame(new_df)

    return new_df

def format_output(row, watson_data):
    """
    Concat user data with watson data.
    """
    processed_row = row

    # get intents pos 1, 2 and 3.
    for i in [0, 1, 2]:
        key_intent = "watson_intent_{}".format(i)
        key_confidence = "watson_confidence_{}".format(i)
        try:
            processed_row[key_intent] = watson_data["intents"][i]["intent"]
            processed_row[key_confidence] = watson_data["intents"][i]["confidence"]
        except:
            processed_row[key_intent] = None
            processed_row[key_confidence] = None
    return processed_row


def send_message(data, message_key, wa):
    """
    Send message to Watson Assistant and apply format_output() function.

    Arguments:
    - data (dict, required): dict with user data.
    - message_key (str, required): The message key on data to be send to Watson.
    - wa (WatsonAssistant object, required): Watson Assistant class.

    Output:
    - Formatted output with user data + watson data.
    """

    logging.info({"message": "Sending message to Watson Assistant."})
    
    watson_data = wa.send_message(data[message_key])
    result = format_output(data, watson_data)
    return result