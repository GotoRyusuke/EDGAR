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
- Last upate: R4/8/28(Nichi)

'''
from bs4 import BeautifulSoup
import pandas as pd
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
        
        results = {'item1a':0, 
                    'item1a_path': '', 
                    'item7':0, 
                    'item7_path': ''}
        for item_name in ['item1a', 'item7']:
            try:
                docs, item_tb = self.strategies.first_method(content)
                item = self.extract_items(docs, item_tb, item_name,1)
            except:
                docs, item_tb= self.strategies.second_method(content)
                item = self.extract_items(docs, item_tb, item_name,2)
            
            if len(item) > 0:
                results[item_name] = 1
                item_filename = item_store_path + '/' + txt_filename + '_' + item_name + '.txt'
                results[item_name + '_path'] = '10-K/' + cik + '/' + txt_filename + '_' + item_name + '.txt'
                
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

        def multi_run(sub_idx_list):
            sub_df = self.panel_df.loc[sub_idx_list,:]
            info_names = list(sub_df.columns)
            for idx in sub_idx_list:
                file = sub_df.loc[idx, 'f_name']
                results = self.export_single_file(file)

                for key, value in results.items():
                    sub_df.loc[idx, key] = value

            original_names = ['item1a', 'item1a_path', 'item7', 'item7_path']
            sub_df = sub_df.loc[:, info_names + original_names]
            new_names = ['I1A_y', 'I1A_adrs', 'I7_y', 'I7_adrs']
            sub_df.columns = info_names + new_names
            
            return sub_df
        
        output_dfs = Parallel(n_jobs=jobs, verbose=1)(delayed(multi_run)(sub_list) for sub_list in idx_list_cut)
        output = pd.DataFrame()
        for sub_df in output_dfs:
            output = pd.concat([output, sub_df])
        output.sort_values(by = ['CIK'], inplace = True)
        output.reset_index(drop = True, inplace = True)

        ''' 
        Note that we separate summary_10K into 2 individual tables, one saving the results for Item 1A
        and the other for Item7. This procedure is specific to my taks and you do not have to follow
        '''
        
        basic_info = ['CIK', 'co_name', 'f_date', 'f_type']
        vars = ['_y', '_adrs']

        i1a_df = output.loc[:, basic_info + ['I1A'+ var for var in vars]]
        i7_df = output.loc[:, basic_info + ['I7'+ var for var in vars]]
        return i1a_df, i7_df

if __name__ == '__main__':
    panel_df_path = 'F:/EDGAR/2022Q2_10-K_sup.xlsx'
    store_path = 'F:/EDGAR/test'
    
    parser = Parsing10K(panel_df_path = panel_df_path,
                        store_path = store_path)
    
    sup_10K, sup10K_ITem7 = parser.threading(2)
