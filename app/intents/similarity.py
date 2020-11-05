import pandas as pd
import datetime
import streamlit as st
from app.helper_functions import *


def ExamplesSimilarity_page(state):
    st.title("Examples similarity")
    st.markdown("""
    Intents must have different examples for the same purpose.

    It's not cool to have the examples too similar in the model, especially if they are in different intents. This confuses your chatbot. :confused:

    Here we'll analyze the similarity between the examples.

    | intent | example | similar example | similar intent | similarity |
    | - | - | - | - | - |
    | #check_order | I want an order status | I want to check my order | #check_order | 0.83 |
    | #check_order | I want to check my order | I want to order something | #place_order | 0.74 |
    | ... | ... | ... | ... |

    Now that you understand the importance of this, let's go to the similarity analysis.
    """)

    sim_option = st.radio('What is our data source?', options=[
        "Watson Assistant", "Import file"])

    if sim_option == "Import file":
        st.markdown("""
        File format

        | intent | example |
        | - | - |
        | I want an order status | #check_order |
        | How to check my order? | #check_order |
        | I want to order | #place_order |

        Without columns names!

        """)

        uploaded_file = st.file_uploader(
            "Attach file", type=["csv", "xlsx"])
        if uploaded_file is not None:
            data = read_df(uploaded_file, cols_names=["examples", "intents"])

    if st.button("Run analysis"):
        from src.intents.similarity import apply_similarity
        if sim_option == "Watson Assistant":
            from src.connectors.watson_assistant import WatsonAssistant
            wa = WatsonAssistant(apikey=state.watson_args["apikey"],
                                 service_endpoint=state.watson_args["endpoint"],
                                 default_skill_id=state.watson_args["skill_id"])

            data = wa.get_intents()
            data = pd.DataFrame(data)

        # Estimate time
        estimate = estimate_time(data["examples"].tolist())

        if estimate["expected_time"] > 120:
            st.warning("You have a lot of data and this generated {combinations} combinations to analyse. Estimated time: {expected_time}".format(
                combinations=estimate["combinations"], expected_time=str(datetime.timedelta(seconds=estimate["expected_time"]))))

        data = apply_similarity(
            data["examples"].tolist(), data["intents"].tolist())

        data = pd.DataFrame(data)
        state.similarity_data = data

    if state.similarity_data is not None:
        data = state.similarity_data
        data.sort_values(by="similarity", ascending=False, inplace=True)

        sim_slider = st.slider('Similarity', min_value=0.0,
                               max_value=1.0, value=(0.8, 1.0), step=0.01)

        data = data[(data["similarity"] >= sim_slider[0]) &
                    (data["similarity"] <= sim_slider[1])]

        st.write("Combinations in the range: {}".format(len(data)))

        link = download_link(data, "similarity.csv", "Download CSV file")
        st.markdown(link, unsafe_allow_html=True)

        st.dataframe(data)

    state.sync()


def estimate_time(examples, each_time=0.000260974):
    import itertools
    combinations = list(itertools.combinations(examples, 2))
    combinations_len = len(combinations)
    expected_time = int(combinations_len * each_time)

    return {"combinations": combinations_len, "expected_time": expected_time}
