""" Categorize Events 
    ThePeppersStudio@gmail.com + Andrew Chase
"""
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import WordPunctTokenizer
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
import pickle

stop_words = stopwords.words('english')
if '__file__' in globals():
    import os
    path = str(os.path.dirname(__file__)) + '/'
else:
    path = ''
category_pickle_path = path + 'categorizer.pkl'

with open(category_pickle_path, 'r') as f:
    classifier = pickle.Unpickler(f).load()
classify = classifier.classify

bag_of_words = lambda words: dict([(word, True) for word in words])
tokens = lambda line: bag_of_words(extract_words(line))

categorize_event = lambda text: classify(tokens(text))


def extract_words(text):
    """
    Extracting features for the classifier
    We want to:
     * Tokenize the text
     * Find the most significant Bigram
     * Remove stopwords
     * Porterstem them
     >>> extract_words("hey yo")
     ['hey', 'yo', 'hey yo']
    """
    stemmer, tokenizer = PorterStemmer(), WordPunctTokenizer()
    tokens = tokenizer.tokenize(text)

    bigram_finder = BigramCollocationFinder.from_words(tokens)
    bigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, 500)
    
    tokens += ["%s %s" % bigram_tuple for bigram_tuple in bigrams]

    stem_long_non_stopwords = \
        lambda tokens: [stemmer.stem(x.lower()) for x in tokens if x not in stop_words and len(x) > 1]
    return stem_long_non_stopwords(tokens)
