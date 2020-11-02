import pandas as pd
import streamlit as st
from app.helper_functions import *


def DecomAnalysis_page(state):
    st.title("Decomposition Analysis")
    st.markdown("""
    When we add a new intent to the model, we want to know how it will fit with our old intents.

    Perhaps the new intent can conflict with old intents. To check how the new intent fit on our model, we use **Decomposition Analysis**.
    
    In this analysis we will understand how the examples and intents are close to each other.
    
    There are 3 algorithms available for you to test.
    """)

    decomposition_method = st.selectbox(
        "Which algorithm do you want to run?", options=['PCA', 'TSNE', 'truncated SVD'])

    if st.button("Run analysis"):
        from src.intents.decomposition_analysis import ExamplesDA, IntentsDA, prepareDataIntents
        from src.connectors.watson_assistant import WatsonAssistant

        wa = WatsonAssistant(apikey=state.watson_args["apikey"],
                             service_endpoint=state.watson_args["endpoint"],
                             default_skill_id=state.watson_args["skill_id"])

        data = wa.get_intents()

        # Decomposition Analysis - Examples
        pca_examples = ExamplesDA(examples=data["examples"], intents=data["intents"],
                                  decomposition_method=decomposition_method)

        if isinstance(state.stopwords, list):
            pca_examples.text_processing(
                stopwords=True, stopwords_file=state.stopwords)

        pca_examples.prepare_data()
        pca_examples.generate_fig(
            title="Examples - Decomposition Analysis ({})".format(decomposition_method))

        # Decomposition Analysis - Intents
        pca_intents = IntentsDA(examples=data["examples"], intents=data["intents"],
                                decomposition_method=decomposition_method)

        pca_intents.data = prepareDataIntents(pca_examples.data)
        pca_intents.generate_fig(
            title="Intents - Decomposition Analysis ({})".format(decomposition_method))

        st.markdown("""
        ## Exemplos - Decomposition Analysis
        We can see the distribution of the examples in a 2D chart.

        Each point in the chart below is an example.
        """)
        st.plotly_chart(pca_examples.fig, use_container_width=True)

        st.markdown("""
        ## Intents - Decomposition Analysis
        We can see the distribution of intents in a 2D chart.

        Each point in the chart below is the average of examples points for each intent.
        """)
        st.plotly_chart(pca_intents.fig, use_container_width=True)

    state.sync()