import streamlit as st
import spacy
import itertools
import warnings
import pandas as pd
from src.intents.nlp_utils.text_preprocessing import normalize_text

def apply_similarity(examples, intents):
    nlp = spacy.load('pt_core_news_md')

    lst = []
    docs = nlp.pipe(examples)
    docs = list(itertools.combinations(docs, 2))
    docs_size = len(docs)

    counter = 0
    pbar = st.progress(0)
    for doc in docs:
        similarity = doc[0].similarity(doc[1])
        intent = intents[examples.index(doc[0].text)]
        similar_intent = intents[examples.index(doc[1].text)]
        result = {"intent": intent, "example": doc[0].text, "similar example": doc[1].text, "similar intent": similar_intent, "similarity": similarity}
        lst.append(result)

        counter += 1
        pbar.progress(counter / docs_size)

    return lst