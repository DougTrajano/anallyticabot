import pandas as pd
import streamlit as st
from app.helper_functions import *

@st.cache
def prepare_logs(logs):
    lst = []
    for log in logs:
        try:
            lst.append({"input": log["request"]["input"]["text"],
            "confidence": log["response"]["intents"][0]["confidence"]})
        except:
            pass
    return lst

def discovery_page(state):
    st.title("Intents Discovery")
    st.markdown("""
    Quando você começa a desenvolver seu chatbot ou até mesmo desenvolver mais intenções, você provavelmente precisará analisar as mensagens dos usuários para mapear as intenções.
    
    Essa atividade é grande parte do trabalho operacional de um desenvolvedor de chatbot, mas aqui nós temos um método para tentar ajudar você.

    Nós utilizaremos um algoritmo não supervisionado de inteligência artificial que tentará agrupar as mensagens dos usuários em tópicos.
    
    O processo é feito em duas etapas:
    - Encontrar o melhor número de tópicos (Number of Clusters, n_clusters)
    - Executar o algoritmo não supervisionado com a melhor divisão encontrada.
    """)
    st.image('images/clusters.gif')
    st.write("Seu trabalho será analisar os exemplos de cada tópico e entender se isto deveria ser uma nova intenção ou não.")

    watson_connected = check_watson(state)

    if watson_connected:
        sim_option = st.radio('Onde vamos buscar as mensagens não atendidas?', options=[
                              "Watson Assistant", "Quero importar um arquivo"])
    else:
        sim_option = "Quero importar um arquivo"

    if sim_option == "Quero importar um arquivo":
        st.markdown("""
        Formato do arquivo

        ```
        quero fazer um pedido
        como cancelar um pedido
        preciso agendar uma visita
        ...
        ```
        """)
        uploaded_file = st.file_uploader(
            "Anexar arquivo", type=["csv", "xlsx"])
        if uploaded_file is not None:
            df = read_df(uploaded_file, cols_names=["examples"])
            unlabeled_examples = df["examples"].tolist()
    elif sim_option == "Watson Assistant":
        # Getting Watson logs
        if not isinstance(state.discovery_data, pd.DataFrame):
            st.write("Buscando logs do Watson Assistant")
            from src.connectors.watson_assistant import WatsonAssistant
            wa = WatsonAssistant(apikey=state.watson_args["apikey"],
                                    service_endpoint=state.watson_args["endpoint"],
                                    default_skill_id=state.watson_args["skill_id"])

            logs = wa.get_logs()
            if len(logs) > 0:
                state.discovery_data = pd.DataFrame(prepare_logs(logs))
            else:
                st.error("Parece que essa skill não possui logs disponíveis.")
                st.stop()
        else:
            data = state.discovery_data
            sim_slider = st.slider('Confiança', min_value=0.0,
                               max_value=1.0, value=(0.3, 0.6), step=0.01)

            data = data[(data["confidence"] >= sim_slider[0]) & (data["confidence"] <= sim_slider[1])]
            st.write(data)
            unlabeled_examples = data["input"].tolist()
            
    if st.button("Executar"):
        st.write("## Trabalhando nos dados")
        st.write("Estamos preparando os dados, isto pode demorar um tempo.")
        
        # Intents Discovery
        from src.intents.discovery import IntentsDiscovery

        # Instantiate an object of IntentsDiscovery class
        intents_discovery = IntentsDiscovery(data=unlabeled_examples)

        # Apply preprocessing on dataset
        if isinstance(state.stopwords, list):
            intents_discovery.text_processing(
                stopwords=state.stopwords, inplace=True)

        # Find best n_clusters
        st.write("Iniciando testes para encontrar o melhor `n_clusters`.")
        intents_discovery.search_n_clusters()

        clustering_data = intents_discovery.clustering(
            n_clusters=intents_discovery.n_clusters)

        df = pd.DataFrame(
            {"examples": clustering_data["data"], "labels": clustering_data["labels"]})

        st.markdown("""
        ## Silhouette score
        Para encontrar o melhor agrupamento usaremos uma métrica chamada [Silhouette](https://en.wikipedia.org/wiki/Silhouette_(clustering)).
        """)

        scores = [e["silhouette_score"] for e in intents_discovery.search_data]
        st.line_chart(pd.DataFrame(
            {"silhouette": scores}), use_container_width=True)

        st.markdown("""
        ## Resultados
        Abaixo você pode conferir os resultados ou baixar um arquivo csv.
        """)

        link = download_link(df, "clustered_examples.csv",
                             "Baixar arquivo csv")
        st.markdown(link, unsafe_allow_html=True)

        st.dataframe(df)

        st.markdown("""
        ## Principais tópicos

        Abaixo podemos ver os principais tópicos que foram encontrados.
        """)

        st.bar_chart(df.groupby("labels").count().sort_values("examples", ascending=True),
                     use_container_width=True)