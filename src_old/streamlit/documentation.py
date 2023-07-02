import streamlit as st
import logging

def documentation_page(state):
    logging.info({"message": "Loading documentation page."})
    st.title("Documentation")
    
    st.markdown("""
    Anallyticabot is a simple data app that offers products for designing, analyzing, and optimizing conversational experiences.

    All Anallyticabot analysis are user-centered based. We provide a gentle introduction in each of them that can help you understand how them works and how them will help you.

    See the Quickstart to get going.
    """)
    
    st.write("""
    # Quickstart

    In this tutorial, you'll get a basic introduction to the Anallyticabot.

    ## Step 1: Connect with Watson Assistant

    Go to the **"Settings"** page and connect with your Watson Assistant skill.
    """)
    
    st.image("images/docs/quickstart_step1.png", width=500)

    st.write("""
    ## Step 2: Settings NLP 
    
    In **"Settings"** page, you can configure the global settings of the platform.

    """)

    st.image("images/docs/quickstart_step2.png", width=500)

    st.write("""
    ## Step 3: Have fun! :smile:
     
    When you are connected with a Watson Assistant skill, you can see all available page in the menu.

    """)

    st.image("images/docs/quickstart_step3.png", width=200)