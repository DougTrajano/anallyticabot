import streamlit as st
import spacy
import itertools
import logging


def apply_similarity(examples, intents):

    logging.info(
        {"message": "Applying similarity for all examples in the skill."})

    nlp = spacy.load('pt_core_news_md')

    docs = nlp.pipe(examples)
    docs = list(itertools.combinations(docs, 2))
    docs.reverse()

    docs_size = len(docs)

    counter = 0
    pbar = st.progress(counter)

    lst = []
    while len(docs) > 0:
        doc = docs.pop()
        similarity = doc[0].similarity(doc[1])
        intent = intents[examples.index(doc[0].text)]
        similar_intent = intents[examples.index(doc[1].text)]
        result = {"intent": intent, "example": doc[0].text, "similar example": doc[1].text,
                  "similar intent": similar_intent, "similarity": similarity}
        lst.append(result)

        counter += 1
        pbar.progress(counter / docs_size)

    return lst


def apply_similarity_intents(examples_lst, intents):

    logging.info({"message": "Applying similarity inside intents."})

    nlp = spacy.load('pt_core_news_md')

    counter = 0
    pbar = st.progress(counter)

    lst = []
    for examples, intent in zip(examples_lst, intents):
        docs = nlp.pipe(examples)
        docs = list(itertools.combinations(docs, 2))

        while len(docs) > 0:
            doc = docs.pop()
            similarity = doc[0].similarity(doc[1])
            result = {"intent": intent, "example": doc[0].text, "similar example": doc[1].text,
                      "similar intent": intent, "similarity": similarity}
            lst.append(result)

        counter += 1
        pbar.progress(counter / len(intents))

    return lst
