import streamlit as st
from src.helper_functions import *

from app.multi_app import *
from app.home import *
from app.intents.counter_examples import *
from app.intents.decomposition_analysis import *
from app.intents.discovery import *
from app.intents.similarity import *
from app.intents.watson_prediction import *
from app.settings import *
from app.documentation import *

parameters = load_parameters("properties/application.json")

st.set_page_config(page_title=parameters["page_title"], layout="wide",
                        page_icon=parameters["page_icon"])

if parameters["disable_streamlit_menu"] == True:
    disable_menu()

app = MultiApp()

app.add_app("Home", main_page)
app.add_app("Intents - Counterexamples", counterexamples_page, logged_page=True)
app.add_app("Intents - Decomposition Analysis", decomposition_page, logged_page=True)
app.add_app("Intents - Discovery", discovery_page, logged_page=True)
app.add_app("Intents - Examples Similarity", similarity_page, logged_page=True)
app.add_app("Intents - Watson Prediction", watson_prediction_page, logged_page=True)
app.add_app("Settings", settings_page)
app.add_app("Documentation", documentation_page)

app.run(title=parameters["page_title"], parameters=parameters)