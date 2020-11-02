import streamlit as st

def main_page(state):
    st.title("Anallyticabot")
    st.write("""
    Anallyticabot is a platform that provides **advanced analytics** to help you improve your chatbot.
    
    Identify and improve your virtual assistant's experiences easily and quickly. Anallyticabot is free to use and is an open source project! :blue_heart:
    """)
    
    st.markdown('# Have questions about your chatbot? <span style="color:#3399FF"><b>Anallyticabot has answers.</b></span>', unsafe_allow_html=True)

    col1, col2, col3 = st.beta_columns(3)

    # https://www.flaticon.com/svg/static/icons/svg/3089/3089686.svg
    # https://www.flaticon.com/svg/static/icons/svg/3043/3043500.svg
    col1.markdown('<img src="https://www.flaticon.com/svg/static/icons/svg/747/747240.svg" style="{ width: 100px; margin-left: auto; margin-right: auto; display: block; text-align: center; }" alt="Save time tracking metrics">', unsafe_allow_html=True)
    col1.markdown("<h2 style='text-align: center;'>Save time tracking metrics</h2>", unsafe_allow_html=True)
    col1.markdown("<span style='text-align: center; display: flex; justify-content: center;'>Replaces patchwork, time-consuming approaches with advanced analytics</span>", unsafe_allow_html=True)

    col2.markdown('<img src="https://www.flaticon.com/svg/static/icons/svg/2274/2274898.svg" style="{ width: 100px; margin-left: auto; margin-right: auto; display: block; text-align: center; }" alt="Improve the end-user experience">', unsafe_allow_html=True)
    col2.markdown("<h2 style='text-align: center;'>Improve the end-user experience</h2>", unsafe_allow_html=True)
    col2.markdown("<span style='text-align: center; display: flex; justify-content: center;'>Helps you make informed product decisions by analyzing interactions with users</span>", unsafe_allow_html=True)
    
    col3.markdown('<img src="https://www.flaticon.com/svg/static/icons/svg/2223/2223109.svg" style="{ width: 100px; margin-left: auto; margin-right: auto; display: block; text-align: center; }" alt="Raise conversion and retention rates">', unsafe_allow_html=True)
    col3.markdown("<h2 style='text-align: center;'>Raise conversion and retention rates</h2>", unsafe_allow_html=True)
    col3.markdown("<span style='text-align: center; display: flex; justify-content: center;'>Provides insights into user journeys so you can take data-driven decisions</span>", unsafe_allow_html=True)

    st.write("""
    # How it works
    
    ## Measure

    The reports tracks bot health metrics (e.g., intents quality, conflicts), measure retention by date or intent.

    ## Analyze

    The Session Flow Report offers a powerful visualization of the most common user journeys. See the most commun intents, complete with usage statistics and exit rates at each conversation turn.

    ## Optimize

    The Messages Report groups similar problematic messages, uncovering functionality gaps. Transcripts are provided for context. For bots at a certain scale, machine learning helps suggest improvements.
    """)
    st.write("""
    # Get started

    - Go to the **"Settings"** page and connect with your Watson Assistant skill.
    - In **"Settings"** page, you can configure the global settings of the platform.
    """)

    st.write("---")

    footer_col1, footer_col2 = st.beta_columns(2)

    footer_col1.subheader("Privacy and Data Stewardship")
    footer_col1.write("We don't record any of your data, all interactions with Anallyticabot are made in real time directly with your Watson Assistant service.")

    footer_col2.subheader("About Anallyticabot")
    footer_col2.write("Anallyticabot is an open source project and is built with care in Porto Alegre, Brazil. :blue_heart: ")
    footer_col2.write("""
    ### Missing something else?
    Open an [issue](https://github.com/DougTrajano/anallyticabot/issues/new/choose) on our GitHub. :)
    """)
    
    state.sync()