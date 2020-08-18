import nltk
import string
import unidecode

def normalize_text(example, stopwords=None):

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
    
    # Strip
    example = example.strip()

    # Lemmatization
    ## Pending
    
    return example