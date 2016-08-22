# coding: utf-8

import pandas as pd
from collections import Counter

jobs = pd.read_csv( 'clean_jobs', encoding = 'utf-8' )

dup = jobs.duplicated()

jobs[~dup].to_csv('unique_jobs.csv', index = False, encoding = 'utf-8')

