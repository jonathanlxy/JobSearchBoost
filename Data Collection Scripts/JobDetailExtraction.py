# Web Parser
from bs4 import BeautifulSoup

# Load requests package to load html pages
# http://stackoverflow.com/questions/2018026/what-are-the-differences-between-the-urllib-urllib2-and-requests-module
import requests 

# Load Regular Expression for complex parsing
import re

# Import codecs in case of encoding issues
import codecs

# Pandas DataFrame for saving data
import pandas as pd
from pandas import DataFrame

# Numpy for random shuffling
import numpy as np

# Pickle to save result
import pickle

# Use OS to get file names
import os

# Import random and sleep to avoid frequent request
import random
import time

##############################################################################

# Function to scrape html content for each url in the list
def html_dump( url_list ):
    # Headers for requests
    headers = { 
                'Accept': 'text/html,application/xhtml+xml,' + \
                'application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch, br',
                'Accept-Language': 'en-US,en;q=0.8,ja;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Host': 'www.linkedin.com',
                'Upgrade-Insecure-Requests': '0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ' + \
                '(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
              }

    html_list = []

    total_url_count = len( url_list )

    for url in url_list:
        # Attempt to get html content
        r = requests.get( url, headers = headers )
        html, status = r.content, r.status_code

        # Detect if LinkedIn bans this scrapping process
        # 200 = Success, other ( maybe 999? ) = block 
        if status == 200:
            html_list.append( html )

            # Check process
            print '%s urls have been processed.' % (
                str( len( html_list ) ) + \
                '/' + \
                str( total_url_count ) 
                )
            ############### DOES NOT WORK ###############
            # # Random sleep to avoid banning
            # if random.random() > .3:
            #     time.sleep( random.randint( 5, 10 ) )
            # else:
            #     time.sleep( 15 )
            # # End of sleep if
            #############################################
        else:
            print '#!' * 20 + '#'
            print 'Request failed at:\n' + url
            print '#!' * 20 + '#'
            break
        # End of status if

    return html_list

# Extract certain elements from raw LinkedIn Job Listing html dump 
def html_to_element( html ):
    # Output element dictionary
    elements = {}

    # Patterns for extracting elements
    patterns = { 
                 'com_industry'    : re.compile( '"formattedIndustries":\[(.*?)\]' ),
                 'com_name'        : re.compile( '"companyName":"(.+?)"' ),
                 'job_title'       : re.compile( '"title":"(.+?)"' ),
                 'job_function'    : re.compile( '"formattedJobFunctions":\[(.*?)\]' ),
                 'job_description' : re.compile( '"description":{"rawText":"(.*?)"' ),
                 'skills'          : re.compile( '"skillsDescription":{"rawText":"(.*?)"' ),
                 'list_date'       : re.compile( '"formattedListDate":"(.*?)"' )
               }

    # Make soup
    soup = BeautifulSoup( html )

    # Extract job detail
    full_detail = soup.find( 'code', id = 'decoratedJobPostingModule' ).string
    
    for key in patterns.keys():
    # Find each meta element in job detail
        try: # If not empty, process element
            match_str = re.findall( patterns[ key ], full_detail )[0]
            elements[ key ] = match_str.strip()

        except IndexError: # If element is missing, return empty list
            elements[ key ] = ''

    return elements

# Merge job details with meta data, save to csv
def job_merge_save( html_list, url_df ):
    # Extract all job description elements
    element_list = [ html_to_element( html ) for html in html_list ]
    # Make it a data frame
    element_df = DataFrame( element_list )
    element_df[ 'job_url' ] = url_df[ 'job_url' ]
    # Merge with url data frame, as a full job detail data frame
    job_df = pd.merge( url_df, element_df, on = 'job_url' )
    job_df.to_csv( 'Jobs/' + f, index = False, encoding = 'utf-8' )

##############################################################################

# 1. Get list of all URL.csv file names 
filelist = os.listdir( 'URL' )
print 'URL files to be scraped:'
print filelist
print '#########################'

# 2. Scraping
for f in filelist:
    print 'Current URL file: ' + f
    
    url_df = pd.read_csv( 'URL/' + f, encoding = 'utf-8')
    # Randomize order to prevent blocking (Might not work, can be commented)
    url_df = url_df.reindex( np.random.permutation( url_df.index ) )

    # Dump html content entirely, defer feature extraction
    html_list = html_dump( url_df['job_url'] ) 

    # Check html list length, early termination requires url df
    # to be cut short, save remaining unscraped URLs
    html_url_diff = len( url_df['job_url'] ) - len( html_list )
    if html_url_diff :
        print 'Url processing halted by LinkedIn.'
        print 'Scrapping process is going to stop.'
        print 'Url scraped: %i\n' %len( html_list )
        url_save = url_df.tail( html_url_diff )
        url_save.to_csv( 'URL/' + f, index=False, encoding = 'utf-8' )
        url_df = url_df.head( len( html_list ) )
    else:
        print 'Url processing successfully finished.\n'
    
    # 
    job_merge_save( html_list, url_df )
    print 'Job info extraction for %s finished.' + 
          'Number of records saved: %i' \
           %(f, len( html_list ) )

    with codecs.open('HTML/' + f, 'wb') as logf:
        pickle.dump(html_list, logf)

    # 4. If halted, quit
    if html_url_diff: 
        break

print 'Scrapping Finished.'