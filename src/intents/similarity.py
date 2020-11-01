import streamlit as st
import spacy
import itertools
import warnings
import pandas as pd

def prepare_data(df):
    intents = df["intents"].unique()
    
    lst = []
    for intent in intents:
        examples = df[df["intents"] == intent]["examples"].tolist()
        lst.append({"intent": intent, "examples": examples})
    return lst

def gen_similarity(intents, stopwords=None):
    from src.intents.nlp_utils.text_preprocessing import normalize_text
    nlp = spacy.load('pt_core_news_sm')

    lst = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        pbar = st.progress(0)
        for i in range(len(intents)):
            docs = itertools.combinations(intents[i]["examples"], 2)
            for doc in docs:
                e1 = nlp(normalize_text(doc[0], stopwords, lemmatizer=True))
                e2 = nlp(normalize_text(doc[1], stopwords, lemmatizer=True))
                similarity = e1.similarity(e2)
                result = {"intent": intents[i]["intent"], "example_1": doc[0], "example_2": doc[1], "similarity": similarity}
                lst.append(result)
            pbar.progress(i / len(intents))

    return lst