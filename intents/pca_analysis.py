# Default libs
import pandas as pd
import numpy as np

# ML libs (PCA)
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
import nltk
from intents.nlp_utils.text_preprocessing import normalize_text, load_stopwords

# Graph libs
import plotly.express as px
import plotly.io as pio

# set default theme
pio.templates.default = "seaborn"

def pcaData(examples, intents):
    
    pipeline = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
    ])     

    X = pipeline.fit_transform(examples).todense()

    pca = PCA(n_components=2).fit(X)
    data2D = pca.transform(X)
    
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
        lst.append({"intent": intent, "x": x, "y": y, "examples_count": examples_count})
    
    df = pd.DataFrame(lst)
    df.sort_values(by=["intent"], inplace=True)
    
    return df

class ExamplesPCA():
    def __init__(self, examples, intents):
        self.examples = examples
        self.intents = intents
        self.examples_processed = None
        self.fig = None
        
    def text_processing(self, stopwords=False, stopwords_file=None):
        if stopwords:
            if isinstance(stopwords_file, str):
                stopwords = load_stopwords(stopwords_file)
            else:
                stopwords = nltk.corpus.stopwords.words('portuguese')
        
        self.examples_processed = [normalize_text(example, stopwords) for example in self.examples]
        
    def generate_fig(self):
        if isinstance(self.examples_processed, list):
            data = pcaData(self.examples_processed, self.intents)
            data["example"] = self.examples
        else:
            data = pcaData(self.examples, self.intents)

        data["example_len"] = [len(example.split()) for example in data["example"]]

        self.fig = px.scatter(data, x="x", y="y",
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

class IntentsPCA():
    def __init__(self, examples, intents):
        self.examples = examples
        self.intents = intents
        self.examples_processed = None
        self.fig = None
        
    def text_processing(self, stopwords=False, stopwords_file=None):
        if stopwords:
            if isinstance(stopwords_file, str):
                stopwords = load_stopwords(stopwords_file)
            else:
                stopwords = nltk.corpus.stopwords.words('portuguese')
        
        self.examples_processed = [normalize_text(example, stopwords) for example in self.examples]
        
    def generate_fig(self, title="Intents Analysis"):
        if isinstance(self.examples_processed, list):
            data = pcaData(self.examples_processed, self.intents)
        else:
            data = pcaData(self.examples, self.intents)
        
        data = prepareDataIntents(data)
        
        self.fig = px.scatter(data, x="x", y="y",
                 size="examples_count", color="intent",
                 hover_name="intent", size_max=10, title=title)
    
    def display(self):
        if self.fig == None:
            self.generate_fig()
            
        self.fig.show()
        
    def export_html(self, file_name="intents_analysis.html"):
        if self.fig == None:
            self.generate_fig()
            
        self.fig.write_html(file_name)