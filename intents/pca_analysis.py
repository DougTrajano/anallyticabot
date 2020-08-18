# Default libs
import pandas as pd
import numpy as np

# ML libs (PCA)
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

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
    df["example_len"] = [len(example.split()) for example in df["example"]]
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

def ExamplesPCA(examples, intents, export_to_html=False):
    data = pcaData(examples, intents)


    fig = px.scatter(data, x="x", y="y",
                     size="example_len", color="intent",
                     hover_name="example", size_max=10, title="Examples Analysis")
    
    if export_to_html:
        if isinstance(export_to_html, str):
            html_name = export_to_html
        else:
            html_name = "examples_analysis.html"
            
        fig.write_html(html_name)
        
    fig.show()

def IntentsPCA(examples, intents, export_to_html=False):
    data = pcaData(examples, intents)
    data = prepareDataIntents(data)

    fig = px.scatter(data, x="x", y="y",
                     size="examples_count", color="intent",
                     hover_name="intent", size_max=10, title="Intents Analysis")
    
    if export_to_html:
        if isinstance(export_to_html, str):
            html_name = export_to_html
        else:
            html_name = "intents_analysis.html"
            
        fig.write_html(html_name)
        
    fig.show()