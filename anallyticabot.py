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

app = MultiApp()

app.add_app("Get Started", main_page)
app.add_app("Intents - Counter examples", irrelevant_examples_page)
app.add_app("Intents - Decomposition Analysis", DecomAnalysis_page)
app.add_app("Intents - Discovery", discovery_page)
app.add_app("Intents - Examples Similarity", ExamplesSimilarity_page)
app.add_app("Settings", settings_page)
app.add_app("Documentation", documentation_page)

app.run(title="Anallyticabot")