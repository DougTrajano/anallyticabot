import time
import pandas as pd
import streamlit as st
from app.helper_functions import *

def counterexamples_page(state):
    st.title("Counterexamples")
    st.markdown("""
    Counterexamples in Watson Assistant are used when we want to avoid answer incorrectly for some user inputs.

    In IBM Cloud it isn't possible to manage counterexamples, you can only add new counerexamples in "Try out".

    We have created this page for you see and delete counterexamples as needed.
    """)
    from src.connectors.watson_assistant import WatsonAssistant
    wa = WatsonAssistant(apikey=state.watson_args["apikey"],
                         service_endpoint=state.watson_args["endpoint"],
                         default_skill_id=state.watson_args["skill_id"])

    # Add new counter example
    counter_example = st.text_input("Add counterexample")

    if st.button("Insert"):
        response = wa.add_counterexamples(counter_example)
        if response["success"]:
            st.success("Counterexample added.")
            time.sleep(state.alert_timeout)
        else:
            st.error("Failed to add the counterexample.")
            time.sleep(state.alert_timeout)

    # Getting counter examples
    counter_examples = wa.get_counterexamples()
    counter_examples = counter_examples["counterexamples"]

    if len(counter_examples) > 0:
        col1, col2 = st.beta_columns(2)
        col1.header("Counterexamples")
        col2.header("Actions")

        for i in range(len(counter_examples)):
            ckey = "counter_examples_{}".format(i)
            col1.write(counter_examples[i])
            cbutton = col2.button("Delete", key=ckey)
            if cbutton:
                pos = int(ckey.split("_")[-1])
                response = wa.delete_counterexamples(counter_examples[pos])
                if response["success"]:
                    st.success("Counterexample deleted.")
                    time.sleep(state.alert_timeout)
                else:
                    st.error("Failed to delete counterexample.")
                    time.sleep(state.alert_timeout)
    else:
        st.markdown(
            "We have no counterexamples in this Watson Assistant skill.")

    state.sync()