# -*- coding: utf-8 -*-
'''
This file helps you to understand how to call the module
Here I suppose you have already summary tables for 10-K
Let us name it as:
    - 10-K: summary_10-K.xlsx

which are saved under the working directory. 
Assume we have saved all the item texts extracted under store

'''
from russia_main import RussiaNum
import pandas as pd
import os

# set working directory
cwd = 'F:/EDGAR/word_freq
os.chdir(cwd)

store_path = 'F:/EDGAR/store'
form = '10-K'
summary_file_path = './summary_10-K.xlsx'

counter = RussiaNum(summary_file_path, store_path = store_path)

for mode in ['lemma', 'exact word']:
    counter.count(mode = mode)
    '''
    use
        df = counter.count(mode = mode) 
    here if you want to check whether the df is really what you want
    
    '''
    counter.save(f'./new_summary_10-K_{mode}.xlsx')



