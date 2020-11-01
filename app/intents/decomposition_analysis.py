import pandas as pd
import streamlit as st
from app.helper_functions import *


def DecomAnalysis_page(state):
    st.title("Decomposition Analysis")
    st.markdown("""
    Sempre que adicionamos uma nova intenção no modelo, queremos saber como ela irá impactar na qualidade do nosso chatbot, seja de forma positiva ou negativa.
    
    Nessa análise nós iremos entender como os exemplos e as intenções estão próximas umas das outras.
    
    Existem 3 algoritmos disponíveis para você testar.
    """)

    if not check_watson(state):
        not_connected_page(state)

    decomposition_method = st.selectbox(
        "Qual algoritmo você deseja executar?", options=['PCA', 'TSNE', 'truncated SVD'])

    if st.button("Executar"):
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
            title="Exemplos - Decomposition Analysis ({})".format(decomposition_method))

        # Decomposition Analysis - Intents
        pca_intents = IntentsDA(examples=data["examples"], intents=data["intents"],
                                decomposition_method=decomposition_method)

        pca_intents.data = prepareDataIntents(pca_examples.data)
        pca_intents.generate_fig(
            title="Intenções - Decomposition Analysis ({})".format(decomposition_method))

        st.markdown("""
        ## Exemplos - Decomposition Analysis
        Aqui nós podemos ver a distribuição dos exemplos em um gráfico bidimensional.

        Cada ponto no gráfico abaixo é um exemplo.
        """)
        st.plotly_chart(pca_examples.fig)

        st.markdown("""
        ## Intenções - Decomposition Analysis
        Aqui nós podemos ver a distribuição das intenções em um gráfico bidimensional.
        
        Cada ponto no gráfico abaixo é a média dos exemplos da intenção.
        """)
        st.plotly_chart(pca_intents.fig)