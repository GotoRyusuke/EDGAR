# -*- coding: utf-8 -*-
'''
DESCRIPTION
-----------
 Using two matching strategies to extract:
    - Part I Item 2. Management's Discussion and Analysis of Financial Condition and Results of Operations
    - PART II Item 1A. Risk Factors
    from 10-Q forms

CONTENTS
--------
- <CLASS> Parsing10Q

OTHER INFO.
-----------
- Last upate: R4/8/20(Do)
- Author: GOTO Ryusuke 
- Contact: 
    - Email: yuhang1012long@link.cuhk.edu.hk (preferred)
    - WeChat: L13079237

'''
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from joblib import Parallel, delayed
from matching_strategies import  cut_unreadable, item_detector

class Parsing10Q:
    def __init__(self,
                panel_df_path: str,
                store_path: str):
        
        self.panel_df_path = panel_df_path
        self.store_path = store_path
        
        self.strategies = item_detector('10-Q')

    def extract_items(self, docs, tb, which: str, st: int):
        if len(tb) == 0: return ''
        item_tb = tb.loc[tb['item'] == which,:]
        
        if which == 'item1a':
            if len(item_tb) == 0: return ''             
            elif len(item_tb) >= 2:
                start_idx = 1
            else:
                start_idx = 0
                
            start_item = item_tb.start.values[start_idx]
            rawtb = tb.loc[tb['start'] > start_item]
            
            if 'item2' in rawtb['item'].values:
                end_item = rawtb.loc[rawtb['item'] == 'item2', 'start'].values[0]
            elif 'item6' in rawtb['item'].values:
                end_item = rawtb.loc[rawtb['item'] == 'item6', 'start'].values[0]
            else: return ''
            
        elif which == 'item2':
            if len(item_tb) == 0: return ''
            elif len(item_tb) > 2:
                start_idx = 2
            elif len(item_tb) == 2:
                start_idx = 1
            else:
                start_idx = 0
                
            start_item = item_tb.start.values[start_idx]
            rawtb = tb.loc[tb['start'] > start_item]
            
            if 'item3' in rawtb['item'].values:
                end_item = rawtb.loc[rawtb['item'] == 'item3', 'start'].values[0]
            elif 'item4' in rawtb['item'].values:
                end_item = rawtb.loc[rawtb['item'] == 'item4', 'start'].values[0]
            elif 'partii' in rawtb['item'].values:
                end_item = rawtb.loc[rawtb['item'] == 'partii', 'start'].values[0]
            elif 'item1a' in rawtb['item'].values:
                end_item = rawtb.loc[rawtb['item'] == 'item1a', 'start'].values[0]
            elif 'item2' in rawtb['item'].values:
                end_item = rawtb.loc[rawtb['item'] == 'item2', 'start'].values[0]
            elif 'item6' in rawtb['item'].values:
                end_item = rawtb.loc[rawtb['item'] == 'item6', 'start'].values[0]
            else: end_item = len(docs)
            
        if st == 1:
            item_raw = docs[start_item:end_item]
            item_content = BeautifulSoup(item_raw, 'lxml')
            
            for table in item_content.find_all('table'):
                if not ('\u2022' in table.get_text()):
                    table.extract()
       
            output = item_content.get_text()
            output = cut_unreadable(output)
        else:
            output = docs[start_item:end_item]
            output = cut_unreadable(output)

        return output

    def export_single_file(self, single_path):
        cik = single_path.split('/')[-1].split('_')[0]
        txt_filename = single_path.split('/')[-1].split('.')[0]
        item_store_path = self.store_path + '/' + cik 
        os.makedirs(item_store_path, exist_ok = True)

        with open(single_path, 'r') as f:
            content = f.read()
        
        results = {'item2':0, 'item1a':0, 
                   'if10k': 0, 'ifnos':0,
                   'item2_path': '', 'item1a_path': ''}
        
        for item_name in ['item2', 'item1a']:
            try:
                docs, item_tb = self.strategies.first_method(content)
                item = self.extract_items(docs, item_tb, item_name,1)
            except:
                docs, item_tb= self.strategies.second_method(content)
                item = self.extract_items(docs, item_tb, 'item',2)
            
            if len(item) > 0:
                results[item_name] = 1
                item_filename = item_store_path + '/' + txt_filename + '_' + item_name + '.txt'
                results[item_name + '_path'] = '10-Q/' + cik + '/' + txt_filename + '_' + item_name + '.txt'
                
                with open(item_filename, 'w') as f:
                    f.write(item)
                    
            if item_name == 'item1a':
                # find 10K
                if '10-K' in item:
                    results['if10k'] = 1
                
                # find 'None' or 'Not Applicable'
                # check if 'None' or 'Not Applicable' appears in the text under item 1a
                rex_none = re.compile(r'[Nn]one|NONE')
                rex_na = re.compile(r'([Nn]ot|NOT)(\s|\n)*([Aa]pplicable|APPLICABLE)')
                
                found_none = rex_none.findall(item)
                found_na = rex_na.findall(item)

                if len(found_none) != 0 or len(found_na) != 0:
                    results['ifnos'] = 1
        return results

    def threading(self, jobs):
        self.panel_df = pd.read_excel(self.panel_df_path)
        idx_list = list(self.panel_df.index)
        num_per_job = int(len(idx_list) / jobs)
        idx_list_cut = []
        for i in range(jobs):
            if i != jobs - 1:
                idx_list_cut.append(idx_list[i * num_per_job: (i + 1) * num_per_job])
            else:
                idx_list_cut.append(idx_list[i * num_per_job:])
        output = pd.DataFrame()
        def multi_run(sub_idx_list):
            sub_df = self.panel_df.loc[sub_idx_list,:]
            for idx in sub_idx_list:
                file = sub_df.loc[idx, 'FileName']
                print(file)
                results = self.export_single_file(file)
                
                values = list(results.values())
                sub_df.loc[idx,['I2_y', 'I1A_y', 
                                'I1A_if10k', 'I1A_ifnos',
                                'I2_adrs', 'I1A_adrs']] = values

            return sub_df
        
        output_dfs = Parallel(n_jobs=jobs, verbose=1)(delayed(multi_run)(sub_list) for sub_list in idx_list_cut)
        for sub_df in output_dfs:
            output = pd.concat([output, sub_df])
        output.sort_values(by = ['CIK'], inplace = True)
        output.reset_index(drop = True, inplace = True)
        return output
    
if __name__ == '__main__':
    store_path = 'F:/EDGAR/Extracted/10-Q'
    panel_df_path = 'F:/EDGAR/2022Q2_10-Q_dropdup.xlsx'
    
    parser = Parsing10Q(panel_df_path,store_path)
    form10q_df = parser.threading(2)
    # form10q_df.to_excel('F:/EDGAR/2022Q2_10-Q_ver2.xlsx', index = False)