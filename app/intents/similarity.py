import pandas as pd
import streamlit as st
from app.helper_functions import *


def ExamplesSimilarity_page(state):
    st.title("Examples similarity")
    st.markdown("""
    As intenções precisam ter exemplos diferentes sobre o mesmo propósito.
    
    Não é legal ter exemplos iguais no modelo, ainda mais se eles estão em intenções diferentes.

    Isto causa problemas no entendimento do seu chatbot. :confused:

    Aqui vamos analisar a similaridade entre os exemplos, veja como:

    |   | Exemplo 1 | Exemplo 2 | Similaridade |
    | - | - | - | - |
    | **#fazer_pedido** | Quero pedir uma pizza | Quero pedir uma pizza grande | 0.85 |
    | ... | ... | ... | ... |
    """)
    watson_connected = check_watson(state)

    st.write("Agora que você já entendeu a importância disto, vamos para a análise.")
    if watson_connected:
        sim_option = st.radio('Onde vamos buscar os exemplos', options=[
                              "Watson Assistant", "Quero importar um arquivo"])
    else:
        sim_option = "Quero importar um arquivo"

    if sim_option == "Quero importar um arquivo":
        st.write("Formato do arquivo")
        st.table(pd.DataFrame({"  ": ["quero fazer um pedido", "como consultar meu pedido"],
                               " ": ["#fazer_pedido", "#consultar_pedido"]}))

        uploaded_file = st.file_uploader(
            "Anexar arquivo (todos os exemplos devem estar na primeira coluna)", type=["csv", "xlsx"])
        if uploaded_file is not None:
            df = read_df(uploaded_file, cols_names=["examples", "intents"])

    if st.button("Executar"):
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
        data.columns = ["Exemplo 1", "Exemplo 2", "Similaridade"]
        data.sort_values(by="Similaridade", ascending=False, inplace=True)

        sim_slider = st.slider('Similaridade', min_value=0.0,
                               max_value=1.0, value=0.8, step=0.01)
        data = data[data["Similaridade"] >= sim_slider]
        link = download_link(data, "similarity.csv", "Baixar arquivo csv")
        st.markdown(link, unsafe_allow_html=True)

        st.table(data)