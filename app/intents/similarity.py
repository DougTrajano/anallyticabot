import pandas as pd
import streamlit as st
from app.helper_functions import *


def ExamplesSimilarity_page(state):
    st.title("Examples similarity")
    st.markdown("""
    Intents must have different examples for the same purpose.

    It's not cool to have the examples too similar in the model, especially if they are in different intents. This confuses your chatbot. :confused:

    Here we'll analyze the similarity between the examples.

    |   | Exemplo 1 | Exemplo 2 | Similaridade |
    | - | - | - | - |
    | **#check_order** | I want an order status | I want to check my order | 0.83 |
    | ... | ... | ... | ... |

    Now that you understand the importance of this, let's go to the similarity analysis.
    """)

    sim_option = st.radio('What is our data source?', options=[
                            "Watson Assistant", "Import file"])
    
    if sim_option == "Import file":
        st.markdown("""
        File format

        | examples | intents |
        | - | - |
        | I want an order status | #check_order |
        | How to check my order? | #check_order |
        | I want to order | #place_order |

        Without columns names!

        """)

        uploaded_file = st.file_uploader(
            "Attach file", type=["csv", "xlsx"])
        if uploaded_file is not None:
            df = read_df(uploaded_file, cols_names=["examples", "intents"])

    if st.button("Run analysis"):
        from src.intents.similarity import prepare_data, gen_similarity
        if sim_option == "Watson Assistant":
            from src.connectors.watson_assistant import WatsonAssistant
            wa = WatsonAssistant(apikey=state.watson_args["apikey"],
                                 service_endpoint=state.watson_args["endpoint"],
                                 default_skill_id=state.watson_args["skill_id"])

            df = pd.DataFrame(wa.get_intents())

        data = prepare_data(df)
        data = gen_similarity(data, stopwords=state.stopwords)
        data = pd.DataFrame(data)
        data.set_index('intent', inplace=True)
        state.similarity_data = data

    if state.similarity_data is not None:
        data = state.similarity_data
        st.write(data)
        data.sort_values(by="similarity", ascending=False, inplace=True)

        sim_slider = st.slider('Similarity', min_value=0.0,
                               max_value=1.0, value=(0.8, 1.0), step=0.01)

        data = data[(data["similarity"] >= sim_slider[0]) & (data["similarity"] <= sim_slider[1])]

        st.write("Combinations in the range: {}".format(len(data)))

        link = download_link(data, "similarity.csv", "Download CSV file")
        st.markdown(link, unsafe_allow_html=True)

        st.dataframe(data)

    state.sync()