"""Home page"""
import streamlit as st
from utils.streamlit import app_init
from utils.settings import settings


app_init()

def main(title: str = settings.STREAMLIT_TITLE):
    """Main function for the home page

    Args:
    - title (str): The title of the page. Defaults to STREAMLIT_TITLE from settings.
    """
    st.title(title)


if __name__ == "__main__":
    main()
