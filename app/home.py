import streamlit as st
import logging

def main_page(state):
    logging.info({"message": "Loading home page."})
    st.title("Anallyticabot")
    
    st.write("""
    Unlock insights from data to create the right AI-powered conversational experiences for customer service.
    
    Anallyticabot is free to use and is an open source project! :blue_heart:
    """)

    st.markdown('# Have questions about your chatbot? <span style="color:#3399FF"><b>Anallyticabot has answers.</b></span>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    c1.markdown('<img src="https://www.flaticon.com/svg/static/icons/svg/747/747240.svg" style="{ width: 100px; margin-left: auto; margin-right: auto; display: block; text-align: center; }" alt="Save time tracking metrics">', unsafe_allow_html=True)
    c1.markdown("<h2 style='text-align: center;'>Save time tracking metrics</h2>", unsafe_allow_html=True)
    c1.markdown("<span style='text-align: center; display: flex; justify-content: center;'>Replaces patchwork, time-consuming approaches with advanced analytics</span>", unsafe_allow_html=True)

    c2.markdown('<img src="https://www.flaticon.com/svg/static/icons/svg/2274/2274898.svg" style="{ width: 100px; margin-left: auto; margin-right: auto; display: block; text-align: center; }" alt="Improve the end-user experience">', unsafe_allow_html=True)
    c2.markdown("<h2 style='text-align: center;'>Improve the end-user experience</h2>", unsafe_allow_html=True)
    c2.markdown("<span style='text-align: center; display: flex; justify-content: center;'>Helps you make informed product decisions by analyzing interactions with users</span>", unsafe_allow_html=True)
    
    c3.markdown('<img src="https://www.flaticon.com/svg/static/icons/svg/2223/2223109.svg" style="{ width: 100px; margin-left: auto; margin-right: auto; display: block; text-align: center; }" alt="Raise conversion and retention rates">', unsafe_allow_html=True)
    c3.markdown("<h2 style='text-align: center;'>Raise conversion and retention rates</h2>", unsafe_allow_html=True)
    c3.markdown("<span style='text-align: center; display: flex; justify-content: center;'>Provides insights into user journeys so you can take data-driven decisions</span>", unsafe_allow_html=True)

    st.write("# How it works")
    
    st.write("""
    ## Measure

    The reports tracks bot health metrics (e.g., intents quality, conflicts), measure retention by date or intent.
    """)

    st.write("""
    ## Analyze

    The Decomposition Analysis offers a powerful 2D visualization of intents model, see the most similar examples and manage your counterexamples quickly.
    """)
    st.image("images/decomposition_analysis_intents.png", width=600)

    st.write("""
    ## Optimize

    Discover new intents using unsupervised machine learning based on unanswered messages or agent transcripts.
    """)
    st.image("images/intents_discovery.png", width=600)

    st.write("---")

    fc1, fc2 = st.columns(2)

    fc1.subheader("Privacy and Data Stewardship")
    fc1.write("We don't record any of your data, all interactions with Anallyticabot are made in real time directly with your Watson Assistant service.")

    fc2.subheader("About Anallyticabot")
    fc2.write("Anallyticabot is an open source project and is built with care in Porto Alegre, Brazil. :blue_heart: ")
    fc2.write("""
    ### Missing something else?
    Open an [issue](https://github.com/DougTrajano/anallyticabot/issues/new/choose) on our GitHub. :)
    """)
    
    state.sync()