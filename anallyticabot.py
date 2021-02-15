import logging

logging.basicConfig(level=logging.INFO)
                  
logging.info({"message": "Anallyticabot started."})

from src.helper_functions import load_parameters

# Dialogs page
from app.dialogs.dialog_flow import dialogflow_page

# Intents page
from app.intents.stop_words import stop_words_page
from app.intents.watson_prediction import watson_prediction_page
from app.intents.similarity import similarity_page
from app.intents.discovery import discovery_page
from app.intents.decomposition_analysis import decomposition_page
from app.intents.counter_examples import counterexamples_page

# Others page
from app.documentation import documentation_page
from app.settings import settings_page
from app.home import main_page
from app.multi_app import MultiApp

parameters = load_parameters("properties/application.json")

app = MultiApp()

app.add_app("Home", main_page)
app.add_app("Dialogs - Dialog Flow", dialogflow_page, logged_page=True)
app.add_app("Intents - Counterexamples", counterexamples_page, logged_page=True)
app.add_app("Intents - Decomposition Analysis", decomposition_page, logged_page=True)
app.add_app("Intents - Discovery", discovery_page, logged_page=True)
app.add_app("Intents - Examples Similarity", similarity_page, logged_page=True)
app.add_app("Intents - Stop Words", stop_words_page, logged_page=True)
app.add_app("Intents - Watson Prediction", watson_prediction_page, logged_page=True)
app.add_app("Settings", settings_page)
app.add_app("Documentation", documentation_page)

app.run(parameters=parameters)