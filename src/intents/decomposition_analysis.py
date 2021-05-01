# Default libs
import pandas as pd
import numpy as np
from src.helper_functions import setup_logger

logger = setup_logger()

SEED = 1993
np.random.seed(SEED)

# ML libs
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
import nltk
import spacy

from src.nlp_utils.text_preprocessing import normalize_text, load_stopwords, apply_tfidf

# Graph libs
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# set default theme
pio.templates.default = "seaborn"


def decomposition_reduction(examples, intents, method="PCA"):
    logger.info({"message": "Initializing decomposition reduction."})
    X = apply_tfidf(examples)

    if method.lower() == "TSNE":
        model = TSNE(n_components=2, random_state=SEED)
    elif method.lower() == "truncated SVD":
        model = TruncatedSVD(n_components=2, random_state=SEED)
    else:
        model = PCA(n_components=2, random_state=SEED)

    data2D = model.fit_transform(X)

    df = pd.DataFrame(data2D, columns=["x", "y"])

    df["example"] = examples
    df["intent"] = intents
    return df


def prepareDataIntents(df):
    unique_intents = list(set(df["intent"]))

    lst = []
    for intent in unique_intents:
        df_temp = df[df["intent"] == intent]
        examples_count = len(df_temp["example"])
        x = np.mean(df_temp["x"].values)
        y = np.mean(df_temp["y"].values)
        lst.append({"intent": intent, "x": x, "y": y,
                    "examples_count": examples_count})

    df = pd.DataFrame(lst)
    return df


class ExamplesDA():
    def __init__(self, examples, intents, decomposition_method="pca"):

        logger.info({"message": "Instantiate ExamplesDA."})

        self.examples = examples
        self.intents = intents
        self.decomposition_method = decomposition_method
        self.examples_processed = None
        self.data = None
        self.fig = None

    def text_processing(self, stopwords=False, stopwords_file=None):
        logger.info({"message": "Processing examples."})
        if stopwords:
            if isinstance(stopwords_file, str):
                stopwords = load_stopwords(stopwords_file)
            else:
                stopwords = nltk.corpus.stopwords.words('portuguese')

        nlp = spacy.load('pt_core_news_md')
        self.examples_processed = [normalize_text(
            example, nlp, stopwords) for example in self.examples]

    def prepare_data(self):
        logger.info({"message": "Preparing data."})
        if isinstance(self.examples_processed, list):
            self.data = decomposition_reduction(
                self.examples_processed, self.intents, method=self.decomposition_method)
            self.data["example"] = self.examples
        else:
            self.data = decomposition_reduction(
                self.examples, self.intents, method=self.decomposition_method)

        self.data["example_len"] = [len(example.split())
                                    for example in self.data["example"]]
        return self.data

    def generate_fig(self, title="Example - Decomposition Analysis"):
        logger.info({"message": "Generating figure."})
        if not isinstance(self.data, pd.DataFrame):
            self.prepare_data()

        data = self.data.copy()

        intents = data["intent"].unique().tolist()
        intents = sorted(intents)

        hover_texts = []
        for i in range(len(self.data)):
            hover_text = "<b>Example:</b> {}<br><b>Example words:</b> {}<br><b>Intent:</b> {}".format(data["example"][i],
                                                                                                      data["example_len"][i],
                                                                                                      data["intent"][i])
            hover_texts.append(hover_text)

        data["hovertext"] = hover_texts

        layout = go.Layout(
            title=title,
            xaxis=go.layout.XAxis(
                # title='Time',
                showticklabels=False),
            yaxis=go.layout.YAxis(
                # title='Age',
                showticklabels=False)
        )

        fig = go.Figure(layout=layout)
        for intent in intents:
            temp = data[data["intent"] == intent].copy()

            fig.add_trace(go.Scatter(
                x=temp["x"], y=temp["y"],
                mode="markers",
                text=temp["example"],
                opacity=0.6,
                name=intent,
                hovertext=temp["hovertext"],
                hoverinfo="text"
            ))

        self.fig = fig

    def display(self):
        logger.info({"message": "Displaying figure."})
        if self.fig == None:
            self.generate_fig()

        self.fig.show()

    def export_html(self, file_name="examples_analysis.html"):
        logger.info({"message": "Exporting to HTML."})
        if self.fig == None:
            self.generate_fig()

        self.fig.write_html(file_name)


class IntentsDA():
    def __init__(self, examples, intents, decomposition_method="pca"):

        logger.info({"message": "Instantiate IntentsDA."})

        self.examples = examples
        self.intents = intents
        self.decomposition_method = decomposition_method
        self.examples_processed = None
        self.data = None
        self.fig = None

    def text_processing(self, stopwords=False, stopwords_file=None):
        logger.info({"message": "Processing examples."})
        if stopwords:
            if isinstance(stopwords_file, str):
                stopwords = load_stopwords(stopwords_file)
            else:
                stopwords = nltk.corpus.stopwords.words('portuguese')

        nlp = spacy.load('pt_core_news_md')
        self.examples_processed = [normalize_text(
            example, nlp, stopwords) for example in self.examples]

    def prepare_data(self):
        logger.info({"message": "Preparing data."})
        if isinstance(self.examples_processed, list):
            examples = self.examples_processed
        else:
            examples = self.examples

        data = decomposition_reduction(
            examples, self.intents, method=self.decomposition_method)
        self.data = prepareDataIntents(data)
        return self.data

    def generate_fig(self, title="Intents - Decomposition Analysis"):
        logger.info({"message": "Generating figure."})
        if not isinstance(self.data, pd.DataFrame):
            self.prepare_data()

        data = self.data.copy()
        data.sort_values(by="intent", inplace=True)

        layout = go.Layout(
            title=title,
            xaxis=go.layout.XAxis(
                # title='Time',
                showticklabels=False),
            yaxis=go.layout.YAxis(
                # title='Age',
                showticklabels=False)
        )
        fig = go.Figure(layout=layout)

        for row in data.to_dict(orient="records"):
            hover_text = "<b>Intent:</b> {}<br><b>Examples count:</b> {}".format(
                row["intent"], row["examples_count"])

            fig.add_trace(go.Scatter(
                x=[row["x"]], y=[row["y"]],
                mode="markers",
                marker_size=[row["examples_count"]],
                text=[row["intent"]],
                opacity=0.6,
                name=row["intent"],
                hovertext=hover_text,
                hoverinfo="text"
            ))

        self.fig = fig

    def display(self):
        logger.info({"message": "Displaying figure."})
        if self.fig == None:
            self.generate_fig()

        return self.fig.show()

    def export_html(self, file_name="intents_analysis.html"):
        logger.info({"message": "Exporting to HTML."})
        if self.fig == None:
            self.generate_fig()

        self.fig.write_html(file_name)
