import spacy
import nltk
import numpy as np
import pandas as pd
import streamlit as st
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from src.nlp_utils.text_preprocessing import normalize_text, apply_tfidf
from src.helper_functions import setup_logger

logger = setup_logger()
SEED = 1993
np.random.seed(SEED)


class IntentsDiscovery:
    def __init__(self, data: list = None, n_clusters: int = None,
                 spacy_model: str = "en_core_web_sm"):

        nltk.download('punkt')

        self.n_clusters = n_clusters
        self.data = data
        self.data_processed = None
        self.search_data = []
        self._stopwords = None
        self.spacy_model = spacy.load(spacy_model)

        logger.info({"message": "Instantiate IntentsDiscovery object.",
                     "n_clusters": n_clusters})
        

    def search_n_clusters(self, data=None, min_n_clusters=2, max_n_clusters=100, step_n_clusters=1, early_stopping=4):
        """

        https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html
        """

        logger.info({"message": "Searching the best n_clusters.", "min_n_clusters": min_n_clusters,
                     "max_n_clusters": max_n_clusters, "step_n_clusters": step_n_clusters, "early_stopping": early_stopping})

        in_search = True
        score_list = []
        for i in range(min_n_clusters, max_n_clusters, step_n_clusters):
            if in_search:
                st.write("Training model to `n_clusters`: {}".format(i))
                temp = self.clustering(
                    data=data, n_clusters=i, apply_cluster_name=False)
                session_data = temp["scores"]
                session_data["n_clusters"] = i
                score_list.append(session_data["silhouette_score"])
                self.search_data.append(session_data)

                if len(score_list) > 2 and isinstance(early_stopping, int):
                    if self.count_early_stopping(score_list) >= early_stopping:
                        in_search = False

                        max_silhouette = max(score_list)
                        for sess in self.search_data:
                            if sess["silhouette_score"] == max_silhouette:
                                self.n_clusters = sess["n_clusters"]

        st.write("We found the best `n_clusters`. Is {}.".format(self.n_clusters))

        return self.n_clusters

    def clustering(self, data=None, n_clusters=None, apply_cluster_name=True):

        logger.info({"message": "Clustering phrases.",
                     "n_clusters": n_clusters, "apply_cluster_name": apply_cluster_name})

        if data != None:
            self.data = data
        elif self.data_processed != None:
            data = self.data_processed
        else:
            data = self.data

        if isinstance(n_clusters, int):
            self.n_clusters = n_clusters
        else:
            n_clusters = self.n_clusters

        X = apply_tfidf(data)

        # Initialize the clusterer with n_clusters value and a random generator for reproducibility.
        clusterer = KMeans(n_clusters=n_clusters, random_state=SEED)
        self.labels = clusterer.fit_predict(X)

        if apply_cluster_name:
            self.get_clusters_name(clean_texts=True)

        self.kmeans_score = clusterer.score(X)
        self.silhouette_score = silhouette_score(X, self.labels)

        return {"scores": {"kmeans_score": self.kmeans_score, "silhouette_score": self.silhouette_score}, "data": self.data, "labels": self.labels}

    def count_early_stopping(self, score_list):

        logger.info({"message": "Checking early stopping policy."})

        max_value = max(score_list)
        list_size = len(score_list)
        max_pos = score_list.index(max_value)

        return list_size - max_pos

    def text_processing(self, stopwords=False, inplace=True):

        logger.info({"message": "Processing text.",
                     "stopwords": stopwords, "inplace": inplace})

        if isinstance(stopwords, list):
            self._stopwords = stopwords
        else:
            self._stopwords = None

        normalized_texts = [normalize_text(
            text, self.spacy_model, self._stopwords) for text in self.data]

        if inplace:
            self.data_processed = normalized_texts
        else:
            return normalized_texts

    def get_ngrams(self, text, n_grams=2):

        logger.info({"message": "Getting n_grams."})

        n_grams = ngrams(word_tokenize(text), n_grams)
        return [' '.join(grams) for grams in n_grams]

    def get_clusters_name(self, clean_texts=True):

        logger.info({"message": "Getting clusters names.",
                     "clean_texts": clean_texts})

        if clean_texts:
            example = [normalize_text(
                text, self.spacy_model, self._stopwords, lemmatizer=False) for text in self.data]
        else:
            example = self.data

        unique_labels = list(set(self.labels))

        df = pd.DataFrame({"example": example, "label": self.labels})

        for label in unique_labels:
            df_temp = df[df["label"] == label].copy()
            ngrams = []

            for example in df_temp["example"].tolist():
                ngrams = ngrams + self.get_ngrams(example)

            if len(ngrams) == 0:
                for example in df_temp["example"].tolist():
                    ngrams = ngrams + self.get_ngrams(example, n_grams=1)

            try:
                cluster_name = pd.Series(
                    ngrams).value_counts().head(1).index[0]
            except:
                cluster_name = "undefined cluster"
            finally:
                df["label"].replace(label, cluster_name, inplace=True)

        self.labels = df["label"].tolist()
