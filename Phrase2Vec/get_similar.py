# -*- coding: utf-8 -*-
'''
DESCRIPTION
-----------
A module to get similar words from a trained model for a given list of words
Two methods:
    1. word-word: get similar words for a given word based on cosine similarity
    2. word-dict: calculate the average wv (AWV) for a given list of words(seed words),
    and calculate cosine similarity between AWV and a given word

For each method, two source of similar words can be used:
    1. words in the model;
    2. words from an external source of words

CONTENTS
--------
- <FUNC> stop_words_load
- <CLASS> get_similar_words

OTHER INFO.
-----------
- Last upate: R4/7/27(Sui)
- Author: GOTO Ryusuke 
- Contact: 
    - Email: yuhang1012long@link.cuhk.edu.hk (preferred)
    - WeChat: L13079237
'''

import os
from gensim.models import word2vec
import pandas as pd
from gensim.models import KeyedVectors
from scipy import spatial
import time
import numpy as np

def stop_words_load(dict_path):
    stop_words_list = []
    stop_words_paths = [dict_path + "/" + file for file in os.listdir(dict_path) if file != ".DS_Store"]
    for s_path in stop_words_paths:
        with open(s_path, "r") as f:
            stop_words_list += [w.split("|")[0].strip().lower() for w in f.read().splitlines()]
    stop_words_list = sorted(set(stop_words_list))
    return stop_words_list

class get_similar_words:
    def __init__(self,
                 model_path: str):
        '''
        To initialise the instance, the path of the model to be used should be given
        
        Parametre
        ---------
        model_path: str
            The path of the model
            
        '''
        print('START INITIALISING...')
        self.model = word2vec.Word2Vec.load(model_path)
        self.word_vectors = self.model.wv
        
        print('INITIALISED SUCCESSFULLY.')
    
    def similar_words_from_model(self, seed_wl: list, topn: int):
        '''
        A method to get similar words from the model for a list of seed words

        Parametres
        ----------
        seed_wl : list
            a list of seed words
        topn: int
            how many similar words want to get

        Returns
        -------
        similar_wns_df: pd.DataFrame
            a df with columns the seed words and rows the similar words as well
            as their respective scores
        similar_w_df: pd.DataFrame
            a df with columns the seed words and rows the similar words

        '''
        
        similar_wns_df = pd.DataFrame()
        similar_w_df = pd.DataFrame()
        
        start_time = time.time()
        for sw in seed_wl:              
            try:
                similar_words_list = []
                similar_words_score_list = []
                for item in self.model.wv.most_similar(sw.lower(), topn = topn):
                    similar_words_list.append(item[0])
                    similar_words_score_list.append(item[1])
                    
                similar_wns_df[sw] = similar_words_list
                similar_w_df[sw] = similar_words_list
                similar_wns_df[sw + '_score'] = similar_words_score_list
                
            except KeyError:
                # similar_wns_df[sw] = np.nan
                # similar_w_df[sw] = np.nan
                # similar_wns_df[sw + '_score'] = np.nan
                continue
        
        print('SIMILAR-WORD FROM MODEL COMPLETED.')
        print('TIME CONSUMPTION: %fs'%(time.time()-start_time))
            
        return similar_wns_df, similar_w_df    
    
    def similar_words_from_wl(self,seed_wl: list, source_wl: list):
        '''
        A method to choose similar words for seed words from another list of words

        Parametres
        ----------
        seed_wl : list
            A list of seed words
        source_wl : list
            A list of words from which the similar words will be chosen

        Returns
        -------
        similar_wns_df: pd.DataFrame
            a df with columns the seed words and rows the similar words as well
            as their respective scores
        similar_w_df: pd.DataFrame
            a df with columns the seed words and rows the similar words

        '''
        
        similar_wns_df = pd.DataFrame()
        similar_w_df = pd.DataFrame()
        
        count = 0
        per = 0
        
        start_time = time.time()
        for word1 in seed_wl:
            count += 1
            if count > len(seed_wl)/100 * per:
                print(f'{per}% done')
                per += 1
            
            w_df = pd.DataFrame(columns = [word1,word1 + '_score'])
            idx = 1
            for word2 in source_wl:
                try:
                    score = self.model.wv.similarity(word1.lower(), word2.lower())
                except KeyError: continue
                w_df.loc[idx,[word1,word1 + '_score']] = [word2,score]
                idx += 1
            
            w_df.sort_values([word1 + '_score'], inplace = True, ascending = False)
            w_df.reset_index(drop = True, inplace = True)
                
            similar_wns_df.loc[:,word1] = w_df[word1]
            similar_wns_df.loc[:,word1+'_score'] = w_df[word1+'_score']
            similar_w_df.loc[:,word1] = w_df[word1]
        
        print('SIMILAR-WORD FROM WORD-LIST COMPLETED.')
        print('TIME CONSUMPTION: %fs'%(time.time()-start_time))
        
        return similar_wns_df, similar_w_df
    
    def similar_words_from_model_AWV(self, seed_wl: list, topn:int):
        '''
        A method to get similar words from the model for a list of seed words.
        AWV will be used

        Parametres
        ----------
        seed_wl : list
            a list of seed words
        topn: int
            how many similar words want to get

        Returns
        -------
        similar_wns_df: pd.DataFrame
            a df with columns the seed words and rows the similar words as well
            as their respective scores
        similar_w_df: pd.DataFrame
            a df with columns the seed words and rows the similar words

        '''
        similar_wns_df = pd.DataFrame()
        similar_w_df = pd.DataFrame()
        
        new_seed_wl = []
        for sw in seed_wl:
            try:
                tmp = self.word_vectors.key_to_index[sw]
                new_seed_wl.append(sw)
            except KeyError: continue
        

        similar_words_list =[]
        similar_words_score_list = []
        
        start_time = time.time()
        for item in self.model.wv.most_similar(new_seed_wl, topn = topn):
            similar_words_list.append(item[0])
            similar_words_score_list.append(item[1])
            
        similar_wns_df["all_dict_mean"] = similar_words_list
        similar_w_df['all_dict_mean'] = similar_words_list
        similar_wns_df["all_dict_mean_score"] = similar_words_score_list
        
        print('SIMILAR-WORD FROM MODEL(AWN) COMPLETED.')
        print('TIME CONSUMPTION: %fs'%(time.time()-start_time))
        
        return similar_wns_df, similar_w_df
    
    def similar_words_from_wl_AWV(self, seed_wl :list, source_wl: list):
        '''
        A method to choose similar words for seed words from another list of words.
        AWV will be used.

        Parametres
        ----------
        seed_wl : list
            A list of seed words
        source_wl : list
            A list of words from which the similar words will be chosen

        Returns
        -------
        similar_wns_df: pd.DataFrame
            a df with columns the seed words and rows the similar words as well
            as their respective scores
        similar_w_df: pd.DataFrame
            a df with columns the seed words and rows the similar words

        '''
        similar_wns_df = pd.DataFrame()
        similar_w_df = pd.DataFrame()
        
        new_seed_wl = []
        
        start_time = time.time()
        for sw in seed_wl:
            try:
                tmp = self.word_vectors.key_to_index[sw]
                new_seed_wl.append(sw)
            except KeyError: continue
        
        seed_word_wvs = pd.DataFrame([self.word_vectors[sw] 
                                      for sw in new_seed_wl]).transpose()
        
        sw_mean_wv = list(seed_word_wvs.mean(axis = 1))
        
        idx = 0      
        for word in source_wl:
            try:
                source_wv = self.word_vectors[word]
            except KeyError:
                continue
            
            score = spatial.distance.cosine(sw_mean_wv, source_wv)
            similar_wns_df.loc[idx, ['word','score']] = word, score
            idx += 1
            
        similar_wns_df.sort_values(['score'], inplace = True)
        similar_wns_df.reset_index(drop = True, inplace = True)
        similar_w_df = similar_wns_df['word']
        
        print('SIMILAR-WORD FROM WL(AWN) COMPLETED.')
        print('TIME CONSUMPTION: %fs'%(time.time()-start_time))
        return similar_wns_df, similar_w_df

if __name__ == '__main__':
    # paths
    lm_path = 'C:/Users/niccolo/Desktop/QLFtask/eastmoney/dicts/LM_expanded_dictV3.xlsx'
    lm_dict = pd.read_excel(lm_path)
    
    sm = list(lm_dict['strong_modal'].dropna())
    wm = list(lm_dict['weak_modal'].dropna())
    ce = list(lm_dict['certainty'].dropna())
    un = list(lm_dict['uncertainty'].dropna())
            
    # load the model & initialise the object
    model_path = 'C:/Users/niccolo/Desktop/QLFtask/eastmoney/word2vec/model/120vec_10win.model'  
    my_get_similar = get_similar_words(model_path = model_path)
    
    # a dict saving the freqs of words in the model
    freq_dict = {}
    for word in  list(my_get_similar.model.wv.index_to_key):
        freq_dict[word] = my_get_similar.word_vectors.get_vecattr(word, 'count')
    
    sw_model_wns, sw_sm_w = my_get_similar.similar_words_from_model_AWV(seed_wl = sm, topn = 2000)
    sw_model_wns, sw_wm_w = my_get_similar.similar_words_from_model_AWV(seed_wl = wm, topn = 2000)
    sw_model_wns, sw_ce_w = my_get_similar.similar_words_from_model_AWV(seed_wl = ce, topn = 2000)
    sw_model_wns, sw_un_w = my_get_similar.similar_words_from_model_AWV(seed_wl = un, topn = 2000)
    
    for ws in [sw_sm_w, sw_wm_w, sw_ce_w, sw_un_w]:
        ws['all_dict_mean'] = [word
                                if word not in sm + ce
                                else np.nan
                                for word in ws['all_dict_mean']]
    
        ws.dropna(inplace = True)
        ws['freq'] = [freq_dict[word] for word in ws['all_dict_mean']]
    
    robust_dict = pd.concat([sw_sm_w, sw_wm_w, sw_ce_w, sw_un_w], axis = 1, ignore_index=True)
    col_names = ['strong_modal','weak_modal', 'certainty', 'uncertainty']
    col_names += [dict_name + '_freq' for dict_name in col_names]   
    robust_dict.columns = col_names                                             
    robust_dict.to_excel('C:/Users/niccolo/Desktop/QLFtask/eastmoney/dicts/LM_expanded_ver3_similar_words.xlsx', index = False)
