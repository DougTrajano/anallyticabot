import streamlit as st
from app.multi_app import *

from app.home import *
from app.intents.counter_examples import *
from app.intents.decomposition_analysis import *
from app.intents.discovery import *
from app.intents.similarity import *
from app.settings import *
from app.documentation import *

st.beta_set_page_config(page_title="Anallyticabot", layout="wide",
                        page_icon="images/icon.ico")

parameters = {
    "alert_timeout": 0.5
}

app = MultiApp()

app.add_app("Home", main_page)
app.add_app("Intents - Counterexamples", counterexamples_page, logged_page=True)
app.add_app("Intents - Decomposition Analysis", DecomAnalysis_page, logged_page=True)
app.add_app("Intents - Discovery", discovery_page, logged_page=True)
app.add_app("Intents - Examples Similarity", ExamplesSimilarity_page, logged_page=True)
app.add_app("Settings", settings_page)
app.add_app("Documentation", documentation_page)

app.run(title="Anallyticabot", parameters=parameters)