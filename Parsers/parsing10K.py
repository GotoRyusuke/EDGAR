# -*- coding: utf-8 -*-
'''
DESCRIPTION
-----------
 Using two matching strategies to extract: 
    - PART I Item 1A. Risk Factors
    - PART II Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations
    from 10-K forms.

CONTENTS
--------
- <CLASS> Parsing10K

OTHER INFO.
-----------
- Last upate: R4/8/8(Getsu)
- Author: GOTO Ryusuke 
- Contact: 
    - Email: 1155169839@link.cuhk.edu.hk (preferred)
    - WeChat: L13079237

'''
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from joblib import Parallel, delayed
from matching_strategies import cut_unreadable, item_detector

class Parsing10K:
    def __init__(self,
                panel_df_path: str,
                store_path: str):
        
        self.panel_df_path = panel_df_path   
        self.store_path = store_path
        self.strategies = item_detector('10-K')
    
    def extract_items(self, docs, tb: pd.DataFrame, which: str, st:int):
        if len(tb) == 0 or which not in tb.item.values: return ''

        item_tb = tb.loc[tb['item'] == which,:]
        
        if len(item_tb) >= 2:
            start_idx = 1
        else:
            start_idx = 0
            
        start_item = item_tb.start.values[start_idx]
        rawtb = tb.loc[tb['start'] > start_item]

        if which == 'item1a':
            if 'item1b' in rawtb.item.values:
                end_item = rawtb.start.values[rawtb.item.values == 'item1b'][0]
            elif 'item2' in rawtb.item.values:
                end_item = rawtb.start.values[rawtb.item.values == 'item2'][0]
            elif 'item3' in rawtb.item.values:
                end_item = rawtb.start.values[rawtb.item.values == 'item3'][0]
            elif 'item4' in rawtb.item.values:
                end_item = rawtb.start.values[rawtb.item.values == 'item4'][0]
            elif 'partii' in rawtb.item.values:
                end_item = rawtb.start.values[rawtb.item.values == 'partii'][0]
            else:
                return ''
        else:
            if 'item7a' in rawtb.item.values:
                end_item = rawtb.start.values[rawtb.item.values == 'item7a'][0]
            elif 'item8' in rawtb.item.values:
                end_item = rawtb.start.values[rawtb.item.values == 'item8'][0]
            elif 'item9' in rawtb.item.values:
                end_item = rawtb.start.values[rawtb.item.values == 'item9'][0]
            elif 'item9a' in rawtb.item.values:
                end_item = rawtb.start.values[rawtb.item.values == 'item9a'][0]
            else:
                return ''
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
    
    def export_single_file(self, single_path: str):
        cik = single_path.split('/')[-1].split('_')[0]
        txt_filename = single_path.split('/')[-1].split('.')[0]
        item_store_path = self.store_path + '/' + cik 
        os.makedirs(item_store_path, exist_ok = True)

        with open(single_path, 'r') as f:
            content = f.read()
        
        results = {'item1a':0, 'item7':0}
        for item_name in list(results.keys()):
            try:
                docs, item_tb = self.strategies.first_method(content)
                item = self.extract_items(docs, item_tb, item_name,1)
            except:
                docs, item_tb= self.strategies.second_method(content)
                item = self.extract_items(docs, item_tb, 'item',2)
                results[item_name] = 1
                item_filename = item_store_path + '/' + txt_filename + '_' + item_name + '.txt'

                with open(item_filename, 'w') as f:
                    f.write(item)
        return results

    def threading(self, jobs: int):
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
                results = self.export_single_file(file)
                
                sub_df.loc[idx,['I1A_y', 'I7_y']] = list(results.values())
                
                if results['item1a'] == 1:
                    sub_df.loc[idx, 'I1A_adrs'] = file.split('.')[0] + '_item1a.txt'
                
                if results['item7'] == 1:
                    sub_df.loc[idx, 'I7_adrs'] = file.split('.')[0] + '_item7.txt'
            
            return sub_df
        
        output_dfs = Parallel(n_jobs=jobs, verbose=1)(delayed(multi_run)(sub_list) for sub_list in idx_list_cut)
        for sub_df in output_dfs:
            output = pd.concat([output, sub_df])
        output.sort_values(by = ['CIK'], inplace = True)
        output.reset_index(drop = True, inplace = True)
        return output

if __name__ == '__main__':
    # store_path = 'F:/EDGAR/Extracted2/10-K'
    store_path = 'F:/EDGAR/TestStore/10-K'
    panel_df_path = 'F:/EDGAR/2022Q2_10-K.xlsx'
    
    parsing10K = Parsing10K(panel_df_path, store_path)    
    form10K_df = parsing10K.threading(4)
    form10K_df.to_excel('F:/EDGAR/2022Q2_10-K_ver2.xlsx', index = False)
