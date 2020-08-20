# Default libs
import pandas as pd
import numpy as np

SEED = 399
np.random.seed(399)

# ML libs
import nltk
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from intents.nlp_utils.text_preprocessing import normalize_text, load_stopwords

# Graph libs
import plotly.io as pio
import plotly.express as px

# set default theme
pio.templates.default = "seaborn"


def decomposition_reduction(examples, intents, method="pca"):
    pipeline = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
    ])

    X = pipeline.fit_transform(examples).todense()

    if method.lower() == "tsne":
        model = TSNE(n_components=2, random_state=SEED)
    elif method.lower() == "truncatedsvd":
        model = TruncatedSVD(n_components=2, random_state=SEED)
    else:
        model = PCA(n_components=2, random_state=SEED)

    data2D = model.fit_transform(X)

    df = pd.DataFrame(data2D, columns=["x", "y"])

    df["example"] = examples
    df["intent"] = intents

    df.sort_values(by=["intent"], inplace=True)
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
    df.sort_values(by=["intent"], inplace=True)

    return df


class ExamplesDA():
    def __init__(self, examples, intents, decomposition_method="pca"):
        self.examples = examples
        self.intents = intents
        self.decomposition_method = decomposition_method
        self.examples_processed = None
        self.data = None
        self.fig = None

    def text_processing(self, stopwords=False, stopwords_file=None):
        if stopwords:
            if isinstance(stopwords_file, str):
                stopwords = load_stopwords(stopwords_file)
            else:
                stopwords = nltk.corpus.stopwords.words('portuguese')

        self.examples_processed = [normalize_text(
            example, stopwords) for example in self.examples]

    def fit(self):
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

    def generate_fig(self):
        if self.data == None:
            self.fit()

        self.fig = px.scatter(self.data, x="x", y="y",
                              size="example_len", color="intent",
                              hover_name="example", size_max=10, title="Examples Analysis")

    def display(self):
        if self.fig == None:
            self.generate_fig()

        self.fig.show()

    def export_html(self, file_name="examples_analysis.html"):
        if self.fig == None:
            self.generate_fig()

        self.fig.write_html(file_name)


class IntentsDA():
    def __init__(self, examples, intents, intents_prefix=None, decomposition_method="pca"):
        self.examples = examples
        self.intents = intents
        self.intents_prefix = intents_prefix
        self.decomposition_method = decomposition_method
        self.examples_processed = None
        self.data = None
        self.fig = None

    def text_processing(self, stopwords=False, stopwords_file=None):
        if stopwords:
            if isinstance(stopwords_file, str):
                stopwords = load_stopwords(stopwords_file)
            else:
                stopwords = nltk.corpus.stopwords.words('portuguese')

        self.examples_processed = [normalize_text(
            example, stopwords) for example in self.examples]

    def fit(self):
        if isinstance(self.examples_processed, list):
            examples = self.examples_processed
        else:
            examples = self.examples

        data = decomposition_reduction(
            examples, self.intents, method=self.decomposition_method)
        self.data = prepareDataIntents(data)
        return self.data

    def generate_fig(self, title="Intents Analysis"):
        if self.data == None:
            self.fit()

        if self.intents_prefix != None:
            self.data["intent_prefix"] = self.intents_prefix
            plotly_color = "intent_prefix"
        else:
            plotly_color = "intent"

        self.fig = px.scatter(self.data, x="x", y="y", hover_name="intent",
                              size="examples_count", color=plotly_color,
                              size_max=10, title=title)

    def display(self):
        if self.fig == None:
            self.generate_fig()

        self.fig.show()

    def export_html(self, file_name="intents_analysis.html"):
        if self.fig == None:
            self.generate_fig()

        self.fig.write_html(file_name)
