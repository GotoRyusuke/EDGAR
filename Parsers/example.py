# -*- coding: utf-8 -*-
'''
- This is a simple example that helps you to understand the work flow of calling EdgarParser.
- Here I suppose that you have downloaded all the raw forms you need and export the info about
CIK, file name(absolute/relative dir included), company name, and filed date to a excel table 
called '10-K_forms_2021Q1-2022Q1.xlsx'
- Let us explore how to call the module and let it parse our 10-K forms and export the summary tables

'''
import pandas as pd
from EdgarParser import edgar_parser

store_path = 'F:/EDGAR/Extracted/10-K'
panel_df_path = 'F:/EDGAR/10-K_forms_2021Q1-2022Q1.xlsx'
summary_df_path = 'F:/EDGAR'

parser = edgar_parser(form_type = '10-K', 
                      store_path = store_path,
                      panel_df_path = panel_df_path)

parser.run(summary_df_path = summary_df_path,
            jobs = 32,
            file_name = 'summary_2021Q1-2022Q2_10-K')

'''
After the parsing is done, there will be two excel files under F:/EDAGR:
    - summary_2021Q1-2022Q2_10-K.xlsx
    - summary_2021Q1-2022Q2_10-K_Item7.xlsx
that save the parsing results for Item 1A and Item 7. The extracted item texts are saved under:
F:/EDGAR/Exatracted/10-K

'''

