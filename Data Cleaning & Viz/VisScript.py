# coding: utf-8

import pandas as pd
import numpy as np

from collections import Counter

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer


jobs = pd.read_csv( 'unique_jobs.csv', encoding = 'utf-8' )
search_terms = jobs.search_term.unique()


### Combine job descriptions with skills
def bind_desc_skill( job ):
    if job[1] is np.nan:
        doc = job[0]
    else:
        doc = ' '.join( job )
    return doc.replace( '\n', ' ' )

jobs['desc_skill'] = jobs[ ['job_description', 'skills'] ].apply( bind_desc_skill, axis = 1 )

### Tokenize job functions & Industry
jobs['job_function'] = jobs['job_function'].apply( lambda j: j.replace( '\"', '' ).split( ',' ) )
jobs['com_industry'] = jobs['com_industry'].apply( lambda j: j.replace( '\"', '' ).split( ',' ) )

### Separate Jobs
jobs_by_term = {}
for term in jobs.search_term.unique():
    jobs_by_term[term] = jobs[ jobs.search_term == term ]
 
### Top Industry
def nestlist2list( nest_list ):
    return [ item for sublist in nest_list for item in sublist ] 
def list_counter( a_list ):
    return pd.Series( ( Counter( a_list ) ), dtype = 'float' )

counter_dic = pd.DataFrame( { 'Ratio(%)': [],
                              'Industry': []
                            } )

for term in jobs_by_term.keys():
    print 'Search Term: %s' %term
    temp_list = list_counter( 
        nestlist2list( 
            jobs_by_term[ term ][ 'com_industry' ] 
        ) 
    ).sort_values( inplace = False, ascending = False 
                 )
    counter_dic = pd.concat( 
        [ counter_dic, 
          pd.DataFrame( { 'Ratio(%)': temp_list / temp_list.sum() * 100,
                          'Industry': temp_list.index,
                          'Term'    : term
                        } ).head( 3 ) 
        ] )
counter_dic.to_csv('IndustryTop3.csv', index = False)

### Date
jobs[ 'list_date' ] = pd.to_datetime(jobs[ 'list_date' ])
pd.DataFrame({'Num_List': Counter(jobs.list_date.apply(lambda d: d.weekday() + 1))}).to_csv('PostDateDensity.csv')