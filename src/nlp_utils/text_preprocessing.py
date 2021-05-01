import string
from unicodedata import normalize
import spacy
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from src.helper_functions import setup_logger

logger = setup_logger()


def normalize_text(example, nlp=None, stopwords=None, lemmatizer=True):
    logger.info({"message": "Normalizing example.", "example": example})
    if nlp == None:
        nlp = spacy.load("pt_core_news_md")

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
    example = normalize('NFKD', example).encode('ASCII','ignore').decode('ASCII')
    example = unidecode.unidecode(example)

    # Lemmatization
    if lemmatizer == True:
        doc = nlp(example)
        example = [token.lemma_ for token in doc]
        example = " ".join(example)

    # Strip
    example = example.strip()

    return example


def load_stopwords(file_name):
    logger.info({"message": "Loading stopwords.", "file_name": file_name})
    with open(file_name) as file:
        stopwords = file.readlines()

    stopwords = [word.strip() for word in stopwords]
    return stopwords


def apply_tfidf(examples):
    logger.info({"message": "Applying TF-IDF.",
                "examples_count": len(examples)})
    pipeline = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
    ])

    X = pipeline.fit_transform(examples).todense()
    return X
