# -*- coding: utf-8 -*-
'''
This file helps you to understand how to call the module
Here I suppose you have already get all summary tables for 3 types of forms
Let us name them as:
    - 10-K: summary_10-K.xlsx
    - 10_K_Item7: summary_10-K_Item7
    - 10-Q: summary_10-Q.xlsx
    - 8-K: summary_8-K.xlsx

which are saved under the working directory. 
Assume we have saved all the item texts extracted under store_path

'''
from russia_main import RussiaNum
import pandas as pd
import os

# set working directory
cwd = 'F:/EDGAR/word_freq'
os.chdir(cwd)

store_path = './store_path'
for mode in ['lemma', 'exact word']:
    os.makedirs(f'./{mode}', exist_ok = True)
    for form_type in ['10-K', '10-K_Item7', '10-Q', '8-K']:
        counter = RussiaNum(summary_file_name = f'./summary_{form_type}.xlsx')
        result = counter.count()
        result.to_excel(f'./{mode}/new_summary_{form_type}.xlsx')


