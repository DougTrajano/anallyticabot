import streamlit as st
import pandas as pd
from src.connectors.watson_assistant import WatsonAssistant


def eval_intent_col(df):
    if "intent" in df.columns:
        if df["intents"].notnull().sum() == 0:
            df.drop(columns=["intents"], errors="ignore", inplace=True)
    return df

@st.cache
def cache_df(df):
    return df

def run_predictions(df, watson_apikey, watson_endpoint, watson_skill):
    """

    """
    wa = WatsonAssistant(apikey=watson_apikey,
                         service_endpoint=watson_endpoint,
                         default_skill_id=watson_skill)
    new_df = []
    
    counter = 0
    pbar = st.progress(counter)

    for row in df.to_dict(orient="records"):
        watson_data = wa.send_message(row["examples"])
        processed_row = format_output(row, watson_data)
        new_df.append(processed_row)
        counter += 1
        pbar.progress(counter / len(df))

    new_df = pd.DataFrame(new_df)

    return new_df


def format_output(row, watson_data):
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
