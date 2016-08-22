# coding: utf-8

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


#### Query URL Assembler
def assemble_url( keywords, locationId, time_range, startcount, listcount ):
    '''
    Syntax:
    keywords: '[word1]+[word2]+[word3]+...'
    locationId: LinkedIn defined location ID
    startcount: Start index of the result
    listcount: Number of result returned
    time_range: anytime='', 
                past 24 hours = '1',
                one_week = '1,2'
                one_month = '1,2,3,4'
    '''
    url_main_body  = 'https://www.linkedin.com/jobs/search?'
    url_keywords   = 'keywords=%s'    %keywords
    url_locationId = '&locationId=%s' %locationId
    url_time_range = '&f_TP=%s'       %'1,2'
    url_start      = '&start=%i'      %startcount
    url_count      = '&count=%i'      %listcount
    
    url = url_main_body  + \
          url_keywords   + \
          url_locationId + \
          url_time_range + \
          url_start      + \
          url_count      + \
          '&trk=jobs_jserp_pagination_2'

    return url


#### Function to Read Query Result Html and Return Job Links
def query_to_link( html ):
    # Parse html
    soup = BeautifulSoup( html, 'lxml' )
    # Extract "JobPostingModule" code chunk, where postings are nested
    job_results = soup.find( 'code', id = 'decoratedJobPostingsModule' ).string.encode( 'utf-8' )
    # Use regex to extract hrefs
    pattern = re.compile( '"viewJobTextUrl":"(.*?)"' )
    hrefs = re.findall( pattern, job_results )
    return hrefs


#### Function to Transfrom Job Links into DataFrame
def make_job_df( keyword, url_list ):
    # Regex is used to extract id in format of .../view/XXXXXXX?....
    id_pattern = re.compile( '.+/view/(\d+)\?.*' )
    
    id_list = [ re.search( id_pattern, job ).group(1) for job in url_list ]
    
    job_list_df = DataFrame( { 'job_id': id_list,
                               'search_term': keyword,
                               'job_url': url_list
                             } 
                           )
    
    return job_list_df


#### Search Terms
keywords = [ 'Data+Scientist', 'Machine+Learning', 'Business+Analytics', 
             'Business+Intelligence']


#### Headers
# Headers are necessary to get 
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


#### Scraping Search Result Job Links
# Default search criteria: 
# 1. NY state (Mostly NYC)
# 2. Last Week
# 3. 50 results
for keyword in keywords:
    print 'Start Scraping...\n'
    start_count = 0
    
    scraping_flag = True
    while scraping_flag:
        print 'Crawling jobs for %s. Current job range: %i to %i' %(
          keyword, start_count, start_count + 50 )
        # Get result html
        query_url = assemble_url( keyword, 'STATES.us.ny', '1,2', start_count, 50 )
        print 'URL:\n%s' %query_url
        
        query_html = requests.get( query_url, headers = headers ).content
        print 'Html extracted.'
        # Save html for debugging
        with codecs.open( 'log_html.html', 'w' ) as f:
            f.write( query_html )
        
        # Extract Links
        job_url_list = query_to_link( query_html )
        
        if ( len( job_url_list ) < 50 ) or ( start_count > 300 ): 
            # If jobs found but less than 50, 
            # or current count exceed limit, quit looping
            scraping_flag = False
        elif len( job_url_list ) > 0:
            # If jobs found more than 50, keep going
            start_count += 50
        else:
            raise ValueError( 'Job list length error! len(job_url_list) = %i' \
                              %len( job_url_list ) )
        
        # Link to DF
        job_url_df = make_job_df( keyword, job_url_list )
        
        # Save Links
        
        filename = 'URL/' + keyword + '.csv'
        
        try:
            # Load archive
            job_url_df_archive = pd.read_csv( filename, dtype={ 'job_id': 'O' } )
            # Combine files
            job_url_df_new = pd.concat( [ job_url_df_archive, job_url_df ] )
            # Remove duplicates and save
            job_url_df_unique = job_url_df_new[ ~job_url_df_new.job_url.duplicated() ]
            job_url_df_unique.to_csv( filename, index = False, encoding = 'utf-8' )
            print 'Job list for %s updated. Current job records for %s: %i' %( 
                  keyword, keyword, job_url_df_unique.shape[0] )
        except IOError:
            print 'No archive found. Creating new file...'
            job_url_df.to_csv( filename, index = False, encoding = 'utf-8' )

print '#'*10
print 'Scraping Completed.'