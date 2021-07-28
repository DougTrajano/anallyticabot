from src.helper_functions import load_parameters, setup_logger
from src.utils.plotly import setup_plotly_theme

logger = setup_logger()
            
logger.info({"message": "Anallyticabot started."})

# Setup plotly theme
setup_plotly_theme()

# Dialogs page
from app.dialogs.dialog_flow import dialogflow_page

# Intents page
from app.intents.stop_words import stop_words_page
from app.intents.watson_prediction import watson_prediction_page
from app.intents.similarity import similarity_page
from app.intents.discovery import discovery_page
from app.intents.decomposition_analysis import decomposition_page
from app.intents.counter_examples import counterexamples_page
from app.intents.utterance_generator import utterances_gen_page

# Metrics page
from app.metrics.conversation import conversation_metrics_page
from app.metrics.intents import intents_metrics_page

# Others page
from app.documentation import documentation_page
from app.settings import settings_page
from app.home import main_page
from app.multi_app import MultiApp

parameters = load_parameters("properties/application.json")

app = MultiApp()

app.add_app("Home", main_page)
app.add_app("Counterexamples Manager", counterexamples_page, logged_page=True)
app.add_app("Decomposition Analysis", decomposition_page, logged_page=True)
app.add_app("Dialog Flow", dialogflow_page, logged_page=True)
app.add_app("Examples Similarity", similarity_page, logged_page=True)
app.add_app("Intents Discovery", discovery_page, logged_page=True)
app.add_app("Metrics - Conversations", conversation_metrics_page, logged_page=True)
app.add_app("Metrics - Intents", intents_metrics_page, logged_page=True)
app.add_app("Stop Words analysis", stop_words_page, logged_page=True)
app.add_app("Utterance generator", utterances_gen_page, logged_page=True)
app.add_app("Watson Prediction", watson_prediction_page, logged_page=True)
app.add_app("Settings", settings_page)
app.add_app("Documentation", documentation_page)

app.run(parameters=parameters)
