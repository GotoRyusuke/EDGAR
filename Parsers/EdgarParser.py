# -*- coding: utf-8 -*-
'''
DESCRIPTION
-----------
 Parse designated type of forms with the help of 3 parsers 

CONTENTS
--------
- <CLASS> edgar_parser

OTHER INFO.
-----------
- Last upate: R4/9/5(Getsu)

'''
import pandas as pd
from parsing8K import Parsing8K
from parsing10K import Parsing10K
from parsing10Q import Parsing10Q

class edgar_parser:
    def __init__(self, 
                form_type: str, 
                store_path: str,
                panel_df_path: str):
        
        self.form_type = form_type
        
        # initialise the parser
        if form_type == '8-K':
            self.parser = Parsing8K(store_path = store_path, panel_df_path = panel_df_path)
        elif form_type == '10-K':
            self.parser = Parsing10K(store_path = store_path, panel_df_path = panel_df_path)
        elif form_type == '10-Q':
            self.parser = Parsing10Q(store_path = store_path, panel_df_path = panel_df_path)  


    def run(self, summary_df_path: str, jobs: int, file_name = None):
        ''' 
        summary_df_path gives the directory where the summary table will be saved,
        and you can customise the file name by inputing a file_name to replace the default one.

        Note that we separate summary_10K into 2 individual tables, one saving the results for Item 1A
        and the other for Item7. This procedure is specific to my taks and you do not have to follow

        '''
        if not file_name:
            file_name = summary_df_path + '/' + file_name
        else:
            file_name = summary_df_path + f'/summary_{self.form_type}'
        
        if self.form_type == '10-K':
            summary_df_I1A, summary_df_I7 = self.parser.threading(jobs = jobs)
            summary_df_I1A.to_excel(file_name + '.xlsx', index = False)
            summary_df_I7.to_excel(file_name + '_Item7.xlsx', index = False)
        else:
            summary_df = self.parser.threading(jobs = jobs)
            summary_df.to_excel(file_name + '.xlsx', index = False)

        