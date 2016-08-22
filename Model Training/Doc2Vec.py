import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
# Best performance
import multiprocessing
# Logging
import time
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
    # Stopwords removal, html special tags included
    custom_stopwords = stopwords.words( 'english' ) + [ 'nbsp', 'amp' ]
    tokens_PS = [ token for token in tokens_P if token not in custom_stopwords ]
    # Stemming
    if stem == True:
        stemmer = PorterStemmer()
        sentence = [ stemmer.stem( token ) for token in tokens_PS ]
    else:
        sentence = tokens_PS
    
    return sentence

def tag_sentence( sentences, tags ):
    for i, line in enumerate( sentences ):
        yield gensim.models.doc2vec.TaggedDocument( line, [ tags[i] ] )

# Jobs
jobs = pd.read_csv( 'unique_jobs.csv', encoding = 'utf-8' )
jobs['desc_skill'] = jobs[ [ 'job_description', 'skills' ] ].apply( bind_desc_skill, axis = 1 )
unique_desc = jobs[ 'desc_skill' ].unique()

# Resume
import codecs
with codecs.open( 'sample_resume.txt', 'r', encoding = 'utf-8' ) as f:
    resume_sentence = make_sentence( f.read(), stem = False )

# Corpus
sentences = map( lambda doc: make_sentence( doc, stem = False ), jobs[ 'desc_skill' ].tolist() )

train = list( tag_sentence( sentences = sentences + [ resume_sentence ],
                            tags = jobs.job_url.tolist() + [ 'resume' ] 
                          )
            )

# Doc2Vec training. This might take a long time to run
d2v_model = gensim.models.doc2vec.Doc2Vec( size = 50, min_count = 2, iter = 10, 
    alpha = 0.025, min_alpha = 0.025, workers = multiprocessing.cpu_count() )

d2v_model.build_vocab( train )

for epoch in range( 10 ):
    print time.ctime()
    print 'Training started. Current epoch: %i' %epoch
    d2v_model.train( train )
    print 'One training round finished. Epoch finished: %i' %epoch
    d2v_model.alpha -= 0.002  # decrease the learning rate
    d2v_model.min_alpha = d2v_model.alpha  # fix the learning rate, no decay

d2v_model.save( 'my_model.doc2vec' )