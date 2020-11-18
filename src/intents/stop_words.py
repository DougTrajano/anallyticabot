from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import unidecode

def get_stop_words(corpus, remove_numbers=False):
    if remove_numbers:
        corpus = remove_numbers_from_corpus(corpus)

    vectorizer = TfidfVectorizer(strip_accents='unicode')
    X = vectorizer.fit_transform(corpus)

    df = pd.DataFrame({"words": vectorizer.get_feature_names(), "idf": vectorizer.idf_})
    cut_off = df.describe().loc['25%'][0]
    df = df[df["idf"] < cut_off]
    df.sort_values(by="idf", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def remove_numbers_from_corpus(corpus):
    new_corpus = []
    for txt in corpus:
        txt = ''.join([i for i in txt if not i.isnumeric()])
        new_corpus.append(txt)
    return new_corpus

def words_count(corpus):
    word_freq = {}
    
    words = ' '
    for txt in corpus:
        words += ' '
        words += unidecode.unidecode(txt)
    words = words.split()

    for word in words:
        if word not in word_freq:
            word_freq[word] = 0 
        word_freq[word] += 1
        
    return word_freq