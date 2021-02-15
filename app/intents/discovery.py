import logging
import pandas as pd
import streamlit as st
from app.helper_functions import *


@st.cache
def prepare_logs(logs):

    logging.info({"message": "Prearing logs."})

    lst = []
    for log in logs:
        try:
            result = {"input": log["request"]["input"]["text"],
                      "confidence": log["response"]["intents"][0]["confidence"]}

            result["input_words"] = len(result["input"].split())
            lst.append(result)
        except:
            pass
    return lst


def discovery_page(state):
    logging.info({"message": "Loading Intents Discovery page."})
    st.title("Intents Discovery")
    
    st.markdown("""
    When you start to develop your chatbot or even you are developing more intents, you will need to analyze user messages to map the new intents.

    This activity is a hard work task for each chatbot developer, but here we have a method to help you.

    We'll use an unsupervised learning algorithm that will try to cluster user messages into topics.

    The process is done in two stages:

    - Find the best number of clusters (n_clusters);
    - Run the unsupervised algorithm with the best number of clusters.
    """)
    st.image('images/clusters.gif')
    st.write("Your job will be analyze the examples of each topic and understand if these examples should be a new intent or not.")

    # Initialize unlabeled_examples
    unlabeled_examples = None

    sim_option = st.radio('Where do we get unlabeled messages?', options=[
        "Watson Assistant", "Import file"])

    if sim_option == "Import file":
        st.markdown("""
        File format

        ```
        I want to make a request
        how to cancel an order
        I need to schedule a visit
        ...
        ```
        """)
        uploaded_file = st.file_uploader(
            "Attach file", type=["csv", "xlsx"])
        if uploaded_file is not None:
            df = read_df(uploaded_file, cols_names=["examples"])
            unlabeled_examples = df["examples"].tolist()
    elif sim_option == "Watson Assistant":
        if st.button("Get logs"):
            # Getting Watson logs
            st.write("Loading Watson Assistant logs.")
            from src.connectors.watson_assistant import WatsonAssistant
            wa = WatsonAssistant(apikey=state.watson_args["apikey"],
                                 service_endpoint=state.watson_args["endpoint"],
                                 default_skill_id=state.watson_args["skill_id"])

            logs = wa.get_logs()
            if len(logs) > 0:
                state.discovery_data = pd.DataFrame(prepare_logs(logs))
            else:
                logging.error({"message": "It's seems that this skill has no logs available."})
                st.error("It's seems that this skill has no logs available.")
                st.stop()

    if isinstance(state.discovery_data, pd.DataFrame):
        if len(state.discovery_data) > 0:
            data = state.discovery_data
            max_words = data["input_words"].max()
            min_words = data["input_words"].min()

            sliders = {
                "confidence": st.slider('Confidence', min_value=0.0,
                                        max_value=1.0, value=(0.3, 0.6), step=0.01),
                "input_words": st.slider('Input words', min_value=max_words,
                                         max_value=max_words, value=(min_words, max_words), step=1)
            }

            data = data[(data["confidence"] >= sliders["confidence"][0]) & (data["confidence"] <= sliders["confidence"][1]) & (
                data["input_words"] >= sliders["input_words"][0]) & (data["input_words"] <= sliders["input_words"][1])]

            st.write("Selected messages: {}".format(len(data)))
            st.write(data)

            unlabeled_examples = data["input"].tolist()

    if unlabeled_examples != None:
        if st.button("Run analysis"):
            st.write("## Working on the data")
            st.write("We are preparing the data, this may take some time.")

            # imports
            import plotly.express as px
            from src.intents.discovery import IntentsDiscovery

            # Instantiate an object of IntentsDiscovery class
            intents_discovery = IntentsDiscovery(data=unlabeled_examples)

            # Apply preprocessing on dataset
            if isinstance(state.stopwords, list):
                intents_discovery.text_processing(
                    stopwords=state.stopwords, inplace=True)

            # Find best n_clusters
            st.write("Starting tests to find the best `n_clusters`.")
            intents_discovery.search_n_clusters()

            clustering_data = intents_discovery.clustering(
                n_clusters=intents_discovery.n_clusters)

            df = pd.DataFrame(
                {"examples": clustering_data["data"], "labels": clustering_data["labels"]})

            st.markdown("""
            ## Silhouette score
            To evaluate how the unsupervised model is performing, we’ll use [Silhouette](https://en.wikipedia.org/wiki/Silhouette_(clustering)) score.
            """)

            df_score = pd.DataFrame(intents_discovery.search_data)

            st.plotly_chart(px.line(df_score, x="n_clusters", y="silhouette_score",
                                    title="Silhouette score"), use_container_width=True)

            st.markdown("""
            ## Clustered messages
            See below the clustered messages or download it as csv file.
            """)

            link = download_link(df, "clustered_examples.csv",
                                 "Download CSV file")

            st.markdown(link, unsafe_allow_html=True)

            st.dataframe(df)

            st.markdown("""
            ## Topics

            Below we can see the topics that were found.
            """)

            df_topics = df.groupby("labels").count()
            df_topics.sort_values("examples", inplace=True, ascending=True)
            df_topics.reset_index(inplace=True)
            
            fig_title = "{} topics for {} messages.".format(len(df_topics), df_topics["examples"].sum())
            fig = px.bar(df_topics, x="examples", y="labels", orientation="h", hover_name="labels", hover_data=["labels"], title=fig_title)
            fig.layout.update(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    state.sync()
