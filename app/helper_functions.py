import base64
import logging
import pandas as pd
import streamlit as st
from src.connectors.watson_assistant import WatsonAssistant


def test_watson_connection(skill_id, apikey, service_endpoint):

    logging.info({"message": "Testing Watson Assistant connection.",
                  "skill_id": skill_id, "apikey": apikey, "service_endpoin": service_endpoint})

    wa = WatsonAssistant(apikey=apikey, service_endpoint=service_endpoint,
                         default_skill_id=skill_id)

    return wa.check_connection()


def not_connected_page(state):
    st.error("Parece que você não está conectado em uma skill do Watson Assistant.")
    st.stop()


@st.cache(allow_output_mutation=True)
def try_read_df(f, cols_names, file_type="csv"):
    try:
        if file_type == "csv":
            data = pd.read_csv(f, names=cols_names)
        else:
            data = pd.read_excel(f, names=cols_names)
    except:
        data = None
    finally:
        return data


def read_df(f, cols_names):
    # csv
    df = try_read_df(f, cols_names, file_type="csv")
    # excel
    if not isinstance(df, pd.DataFrame):
        df = try_read_df(f, cols_names, file_type="xlsx")

    if not isinstance(df, pd.DataFrame):
        df == None
        st.error(
            'Falha ao carregar arquivo. Veja a sessão "Enviando arquivos" na documentação.')
        st.stop()
    return df


def check_df(df):
    if len(df) == 0:
        st.stop()


def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def check_watson(state):
    watson_connected = False
    if isinstance(state.watson_args, dict):
        if state.watson_args.get("connected") == True:
            watson_connected = True
    return watson_connected
