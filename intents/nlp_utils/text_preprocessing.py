import nltk
import string
import unidecode
import spacy
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline

nlp = spacy.load("pt_core_news_lg")

def normalize_text(example, stopwords=None, lemmatizer=True):

    # Lower string
    example = example.lower()
    
    # Remove punctuation
    punctuation = string.punctuation
    example = [ch for ch in example if ch not in punctuation]
    example = "".join(example)

    # Remove stopwords
    if isinstance(stopwords, list):
        example = [e for e in example.split() if e not in stopwords]
        example = " ".join(example)
    
    # Remove unidecode
    example = unidecode.unidecode(example)
    
    # Lemmatization
    if lemmatizer:
        doc = nlp(example)
        example = [token.lemma_ for token in doc]
        example = " ".join(example)
    
    # Strip
    example = example.strip()
    
    return example

def load_stopwords(file_name):
    with open(file_name) as file:
        stopwords = file.readlines()

    stopwords = [word.strip() for word in stopwords]
    return stopwords

def apply_tfidf(examples):
    pipeline = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
    ])

    X = pipeline.fit_transform(examples).todense()
    return X