# -*- coding: utf-8 -*-
'''
DESCRIPTION
-----------
 Using two matching strategies to extract:
    - Item 2.02 Results of Operations and Financial Condition;
    - Item 7.01 Regulation FD Disclosure;
    - Item 8.01 Other Events;
    - Exhibit 99.1
    from an 8-K forms.

CONTENTS
--------
- <CLASS> Parsing8K

OTHER INFO.
-----------
- Last upate: R4/8/8(Getsu)
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

class Parsing8K:
    def __init__(self, panel_df_path: str, store_path: str):
        
        self.panel_df_path = panel_df_path
        self.store_path = store_path
        
        # initialise an item_detector instance as an attributes of a Parsing8K object
        self.strategies = item_detector('8-K')
        
    def extract_items(self, docs:str, tb, which: str, st: int):
        '''
        A method to extract the content of a certain item from the raw XML codes.

        Parameters
        ----------
        docs : str
            The raw XML codes included in a <DOCUMENT></DOCUMENT> tag. 
            Input a string created by one of the strategies in item_detector module,
            i.e., raw_content.
            
        tb : pandas.DataFrame
            A dataframe including the name, start, and end of items in an 8-K form.
            Input a pd df created by one of the strategies in item_detector module.
            i.e., out_tb.
            
        which : str
            Which item to be extractd. In the case of an 8-K form. The input should be one
            of the following:
                i. item202;
                ii. item701;
                iii. item801.
                
        st : int
            Which strategy to be used in finding the start and end of a certain item.
            The input should be one of the following:
                i. 1 if the first strategy to be used;
                ii. 2 if the second strategy to be used.

        Returns
        -------
        output : str
            The content of the item desired.

        '''
        if len(tb) == 0 or which not in tb.item.values: return ''
        
        # find how many tags of the item to be extracted are found
        item_tb = tb.loc[tb['item'] == which,:]
        
        if len(item_tb) >= 2:
            '''
            If more than 2 tags of the item are found, the first one is the tag
            in the table of contents in most cases, so use the second.
            
            On the other, if only one tag is found, most possibly there is no
            table of contents in the form, so just use the only one found.
            
            '''
            start_idx = 1
        else:
            start_idx = 0
        
        # set the start of the item in the string
        start_item = item_tb.start.values[start_idx]
        
        '''
        To find the end of the item, look at the tags whose starts have the indices
        larger than the start we just set.
        
        '''
        rawtb = tb.loc[tb['start'] > start_item]
        
        '''
        In the following block of codes, find the end of the item by checking the 
        start of the item that is most possible to appear after the item we need 
        one by one.
        
        '''
       
        # find item 2.02
        if which == 'item202':
             if 'item501' in rawtb.item.values:
                 end_item = rawtb.start.values[rawtb.item.values == 'item501'][0]
             elif 'item507' in rawtb.item.values:
                 end_item = rawtb.start.values[rawtb.item.values == 'item507'][0]
             elif 'item701' in rawtb.item.values:
                 end_item = rawtb.start.values[rawtb.item.values == 'item701'][0]
             elif 'item801' in rawtb.item.values:
                 end_item = rawtb.start.values[rawtb.item.values == 'item801'][0]
             elif 'item901' in rawtb.item.values:
                 end_item = rawtb.start.values[rawtb.item.values == 'item901'][0]
             else:
                 end_item = len(docs)   
        # find item 7.91
        elif which == 'item701':
             if 'item801' in rawtb.item.values:
                 end_item = rawtb.start.values[rawtb.item.values == 'item801'][0]
             elif 'item901' in rawtb.item.values:
                 end_item = rawtb.start.values[rawtb.item.values == 'item901'][0]
             else:
                 end_item = len(docs)
        # find item 8.01
        elif which == 'item801':
             if 'item901' in rawtb.item.values:
                 end_item = rawtb.start.values[rawtb.item.values == 'item901'][0]
             else:
                 end_item = len(docs)
        '''
        The final extraction procedure differs due to the strategy we use. For
        the first strategy, we remove all data tables from the XML code section
        for the item we need, extract the content from XML codes that constitute
        the item in a form, and finally apply cut_unreadable.
        
        In the case of the second strategy, as the data tables have already been
        removed when applying the strategy and creating the raw_content, what 
        remains is just applying cut_unreadable.
        
        '''
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
        '''
        A method to export the items needed in an 8-K form, if found, to a directory 

        Parameters
        ----------
        single_path : str
            The path of the the file. Should be in txt format.

        Returns
        -------
        results : dict
            A dict saving the result of the extraction for each item found.
            In the case of an 8-K form, it contains:
                - ex991: = 1 if Exhibit 99.1 found and extracted;
                - if_ex991: = 1 if the word 'Exhibit 99.1' found in any of the other item(s) found;
                - item202: = 1 if Item 2.02 found and extracted;
                - item701: = 1 if Item 7.01 found and extracted;
                - item801: = 1 if Item 8.01 found and extracted.

        '''
        
        '''
        The following block consists of some info needed to export the item 
        content to txt file.
        
        '''
        cik = single_path.split('/')[-1].split('_')[0]
        txt_filename = single_path.split('/')[-1].split('.')[0]
        item_store_path = self.store_path + '/' + cik 
        os.makedirs(item_store_path, exist_ok = True)
        
        with open(single_path, 'r') as f:
            content = f.read()
        
        # extract Exhibit 99.1 and export, if found
        flag_ex991 = 0
        ex991 = item_detector.get_ex991(content)
        if len(ex991) > 0:
            flag_ex991 = 1
            ex991_filename = item_store_path + '/' + txt_filename + '_ex991.txt'
            with open(ex991_filename, 'w') as f:
                f.write(ex991)
                
        # a dummy to indicate whether the word 'Exhibit 99.1' is mentioned in 
        # any of the other items found
        
        # extract and export item 2.02, item 7.01, and item 8.01, if found
        results = {'ex991':0,'if_ex991':0,
                   'item202':0, 'item701':0,'item801':0,
                   'item202_991': 0,'item701_991': 0,'item801_991': 0}
        
        flag_if991 = 0
        for item_name in ['item202', 'item701', 'item801']:
            try:
                docs, item_tb = self.strategies.first_method(content)
                item = self.extract_items(docs, item_tb, item_name,1)
            except:
                docs, item_tb= self.strategies.second_method(content)
                item = self.extract_items(docs, item_tb, 'item',2)
            item_if_ex991 = 0
            if len(item) > 0:
                # export only when the length of the content is larger than zero
                
                # check if the word 'Exhibit 99.1' is mentioned in the content
                if 'Exhibit 99.1' in item:
                    flag_if991 += 1
                    item_if_ex991 = 1
                results[item_name] = 1
                item_filename = item_store_path + '/' + txt_filename + '_' + item_name + '.txt'
                with open(item_filename, 'w') as f:
                    f.write(item)
                results[item_name + '_991'] = item_if_ex991
                    
            results['ex991'] = flag_ex991
            if flag_if991 > 0:
                results['if_ex991'] = 1 

            
        return results
    
    def threading(self, jobs: int):
        '''
        Use threading to process a list of files.

        Parameters
        ----------
        jobs : int
            Num. of threads to assign.

        Returns
        -------
        output: pandas dataframe
            A pd df saving the CIK, filename, filing date, results of extraction, and path of item content extracted successfully.

        '''
        
        # read the panel data
        self.panel_df = pd.read_excel(self.panel_df_path)
        
        # get the index of the panel data df
        idx_list = list(self.panel_df.index)
        num_per_job = int(len(idx_list) / jobs)
        
        '''
        To apply threading, first cut the list of indices into some sub-lists;
        the length of each sub-list is dependent of the jobs we assign.
        
        '''
        idx_list_cut = []
        for i in range(jobs):
            if i != jobs - 1:
                idx_list_cut.append(idx_list[i * num_per_job: (i + 1) * num_per_job])
            else:
                idx_list_cut.append(idx_list[i * num_per_job:])
                
        # create an empty df to save the result
        output = pd.DataFrame()
        
        # the func to be run in each thread
        def multi_run(sub_idx_list):
            sub_df = self.panel_df.loc[sub_idx_list,:]
            for idx in sub_idx_list:
                file = sub_df.loc[idx, 'FileName']
                results = self.export_single_file(file)
                
                values = list(results.values())
                
                # fill in the results of extraction
                sub_df.loc[idx,['Ex991_y', 'Ex991_any', 
                                'I202_y', 'I701_y', 'I801_y',
                                'I202_if991','I701_if991','I801_if991']] = values
                
                if results['ex991'] == 1:
                    sub_df.loc[idx, 'Ex991_adrs'] = '8-K' + file.split('.')[0].split('/')[-1] + '_ex991.txt'
                    
                if results['item202'] == 1:
                    sub_df.loc[idx, 'I202_adrs'] = '8-K/' + file.split('.')[0].split('/')[-1] + '_item202.txt'
                
                if results['item701'] == 1:
                    sub_df.loc[idx, 'I701_adrs'] = '8-K/' + file.split('.')[0].split('/')[-1] + '_item701.txt'
                
                if results['item801'] == 1:
                    sub_df.loc[idx, 'I801_adrs'] = '8-K/' + file.split('.')[0].split('/')[-1] + '_item801.txt'
            
            return sub_df
        
        # apply threading
        output_dfs = Parallel(n_jobs=jobs, verbose=5)(delayed(multi_run)(sub_list) for sub_list in idx_list_cut)
        
        # aggregate sub-dfs created by the threading
        for sub_df in output_dfs:
            output = pd.concat([output, sub_df])
            
        output.sort_values(by = ['CIK'], inplace = True)
        output.reset_index(drop = True, inplace = True)
        return output

if __name__ == '__main__':
    store_path = 'F:/EDGAR/Extracted/8-K'
    panel_df_path = 'F:/EDGAR/2022Q2_8-K.xlsx'
    
    parser = Parsing8K(panel_df_path, store_path)
    form8k_df = parser.threading(4)
    # form8k_df.to_excel('F:/EDGAR/2022Q2_8-K_ver2.xlsx', index = False)
    
    # change var names
    # remove duplicates
        
