import pandas as pd
import streamlit as st
from app.helper_functions import *
from src.intents.stop_words import *
from src.helper_functions import setup_logger

logger = setup_logger()

def stop_words_page(state):
    logger.info({"message": "Loading Stopwords page."})
    st.title("Stop Words")
    
    st.markdown("""
    Stop words usually refers to the most common words in a language, there is no single universal list of stop words used by all natural language processing tools.
    
    The reason why stop words are critical to many applications is that, if we remove the words that are very commonly used in a given language, we can focus on the important words instead.

    Unfortunately, almost all projects use lists of irrelevant words provided by [spaCy](https://spacy.io/) or [NLTK](http://www.nltk.org/) that are general and not specific to each context.

    With this in mind, this tool will help you identify words in a list of phrases that probably can be used as stop words in your specific context.
    """)

    st.write("## Import file")
    st.markdown("""
        File format

        ```
        I want to make a request
        how to cancel an order
        I need to schedule a visit
        ...
        ```
        """)

    df_sw = None

    remove_numbers = st.checkbox('Not consider numbers')

    uploaded_file = st.file_uploader(
        "Attach file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        df = read_df(uploaded_file, cols_names=["examples"])
        corpus = df["examples"].tolist()
        if len(corpus) > 0:
            df_sw = get_stop_words(corpus, remove_numbers)
            words_freqs = words_count(corpus)
    
    if isinstance(df_sw, pd.DataFrame):
        from wordcloud import WordCloud

        # Prep Word Cloud
        wc_dict = {}
        for word in df_sw["words"].tolist():
            word_count = words_freqs.get(word)
            if isinstance(word_count, int):
                wc_dict[word] = word_count
        wc = WordCloud(background_color="white", width=1920, height=1024).fit_words(wc_dict)

        # Download
        link = download_link(pd.DataFrame({"stop_words": df_sw["words"].tolist()}), "stop_words.csv", "Download CSV file with stopwords")
        st.markdown(link, unsafe_allow_html=True)

        st.write("## Word Cloud (stop words)")
        st.image(wc.to_array(), use_column_width=True)

    state.sync()
