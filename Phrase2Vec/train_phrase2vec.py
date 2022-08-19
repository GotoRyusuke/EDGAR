# -*- coding: utf-8 -*-
'''
A series of modules to do the following things:
1. cut the content in every single file into sentences, eliminates the punctuations,
and converts all letters into lower case
2. eliminate stop words, merge into a single txt file
3. run word2vec on the file

This file is for task 2

'''
import os
from gensim.models import word2vec, Phrases
from gensim.models.phrases import ENGLISH_CONNECTOR_WORDS
import pandas as pd
import numpy as np

model_path = "./10k_phrase2vec_model"
if not os.path.exists(model_path):
    os.mkdir(model_path)
    
talk_sentence_path = "./cleaned_all_code_content.txt"
model_name = model_path + "/model1.moddel"
small_dict_similar_df_name = "./rus_dict.xlsx"
    

sg = 0 
hs = 0 
vector_size = 120 
window_size = 10  
min_count = 25  
workers = 32  
epochs = 20  
batch_words = 100000

common_texts = word2vec.LineSentence(talk_sentence_path)
bigram_transformer = Phrases(common_texts, min_count=5, threshold=1, connector_words=ENGLISH_CONNECTOR_WORDS)

train_data = bigram_transformer[common_texts]
model = word2vec.Word2Vec(
    train_data,
    min_count=min_count,
    vector_size=vector_size,
    workers=workers,
    epochs=epochs,
    window=window_size,
    sg=sg,
    hs=hs,
    batch_words=batch_words
)

model.save(model_name)
