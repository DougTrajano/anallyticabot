from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def get_stop_words(corpus):
    vectorizer = TfidfVectorizer(strip_accents='unicode')
    X = vectorizer.fit_transform(corpus)

    df = pd.DataFrame({"words": vectorizer.get_feature_names(), "idf": vectorizer.idf_})
    cut_off = df.describe().loc['75%'][0]
    df = df[df["idf"] < cut_off]
    df.sort_values(by="idf", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df