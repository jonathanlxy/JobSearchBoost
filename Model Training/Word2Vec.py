# coding: utf-8
import multiprocessing
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
import gensim

def bind_desc_skill( job ):
    if job[1] is np.nan:
        return job[0]
    else:
        return ' '.join( job )
    
def make_sentence( doc, stem = True ):
    low_doc = doc.lower()
    # Punctuation removal
    tokenizer = RegexpTokenizer( r'\w+' )
    tokens_P = tokenizer.tokenize( low_doc )
    # Stopwords removal
    custom_stopwords = stopwords.words( 'english' ) + [ 'nbsp', 'amp' ]
    tokens_PS = [ token for token in tokens_P if token not in custom_stopwords ]
    # Stemming
    if stem == True:
        stemmer = PorterStemmer()
        sentence = [ stemmer.stem( token ) for token in tokens_PS ]
    else:
        sentence = tokens_PS
    
    return sentence

jobs = pd.read_csv( 'unique_jobs.csv', encoding = 'utf-8' )
jobs[ 'desc_skill' ] = jobs[ [ 'job_description', 'skills' ] ].apply( bind_desc_skill, axis = 1 )

descriptions = map( lambda doc: make_sentence( doc, stem = False ), jobs[ 'desc_skill' ].tolist() )

### Train Word2Vec Model
w2v_model = gensim.models.Word2Vec( descriptions, min_count = 2, workers = multiprocessing.cpu_count() )
# Save it
w2v_model.save( 'my_model.word2vec' )