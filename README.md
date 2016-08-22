# JobSearchBoost
Use web scraping techniques and text analytics to help your job searching

This repository stores all the source code used for my Web Scraping project http://blog.nycdatascience.com/student-works/use-data-science-to-boost-your-job-hunting/

If you do not wish to collect data yourself, please feel free to use __unique_jobs.csv__ for your analysis. This file contains 2500+ job postings scraped from LinkedIn job listing.
__Please note that Job IDs are not unique since different search terms may return same job postings__

### Before running each script, please review the code and make sure data files (e.g. unique_jobs.csv) have been placed in the correct locations

## Data Collection Scripts/
Scripts used to scrape job listings from LinkedIn. 
1. Use JobLinkCollection.py to collect job URLs
2. Use JobDetailExtraction.py to open each URL and extract job details. HTML files will also be saved into /HTML folder in case of unexpected interruptions
3. Use Remove_Duplicate_Job.py to remove duplicated job records

## Data Cleaning & Viz/
This folder contains the Python script (VisScript.py) to extract summary data from main dataset, save as .csv file for R to make visualization plots (Vis.R)

## Model Training/
This folder contains Python scripts to train Word2Vec and Doc2Vec models using collected job data.
