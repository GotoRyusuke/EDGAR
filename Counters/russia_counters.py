# -*- coding: utf-8 -*-
import pandas as pd
from collections import Counter

def cut_sentence(talk_content):
    talk_sentences = []
    talk_words = talk_content.split()
    last_sentence_idx = 0
    exception_rule = ["Mr", "Mrs", "Miss", "Ms", "Sir", "Madam", "Dr", "Cllr", "Lady", "Lord", "Professor", "Prof",
                      "Chancellor", "Principal", "President", "Master", "Governer", "Gov", "Attorney", "Atty"]
    for w_i in range(len(talk_words)):
        talk_word = talk_words[w_i]
        if w_i == len(talk_words) - 1:
            talk_sentences.append(" ".join(talk_words[last_sentence_idx: w_i + 1]))
        else:
            if talk_word[-1] in [".", "?", "!"]:
                if talk_word[:-1] not in exception_rule:
                    if talk_words[w_i + 1][0].isupper():
                        talk_sentences.append(" ".join(talk_words[last_sentence_idx: w_i + 1]))
                        last_sentence_idx = w_i + 1
    return talk_sentences

def find_first_word_index(phrases: list, sentence: list):
    first_words_index_dict = {}
    for phrase in phrases:
        first_word_star = phrase[0]
        if first_word_star not in first_words_index_dict.keys():
            first_word_index = []
            if '*' in first_word_star:
                first_word = first_word_star.split('*')[0]
                for w_i in range(len(sentence)):
                    w = sentence[w_i]
                    if w[:len(first_word)] == first_word:
                        first_word_index.append(w_i)
            else:
                first_word = first_word_star
                for w_i in range(len(sentence)):
                    w = sentence[w_i]
                    if w == first_word:
                        first_word_index.append(w_i)
            first_words_index_dict[first_word_star] = first_word_index
    return first_words_index_dict

def phrase_in_sentence(phrase: list,  first_word_index: list, sentence: list):
    for f_idx in first_word_index:
        flag = True
        for kw_i in range(len(phrase)):
            if f_idx + kw_i >= len(sentence):
                return False
            kw = phrase[kw_i]
            if '*' in kw:
                kw = kw.split('*')[0]
            
                if sentence[f_idx+kw_i][:len(kw)] != kw:
                    flag = False
                    break
            else:
                if sentence[f_idx+kw_i][:len(kw)] != kw:
                    flag = False
                    break
                
        if flag:
            return True
    return False

def count_words_in_text(words_list, text_words):
    dict_count = 0
    words_counter = dict(Counter(text_words))
    counter_keys = list(words_counter.keys())
    
    for words in words_list:
        if len(words) == 1:
            kw = words[0]  
            if '*' not in kw:
                if words[0] in words_counter.keys():
                    dict_count += words_counter[words[0]]
            else:
                kw = kw.split("*")[0]
                for key in counter_keys:
                    if key[:len(kw)] == kw:
                        dict_count += words_counter[key]
        else:
            for w_i in range(len(text_words)):
                flag = True
                for p_w_i, p_w in enumerate(words):
                    if '*' not in p_w:
                        if w_i + p_w_i >= len(text_words) or p_w != text_words[w_i + p_w_i]:
                            flag = False
                            break
                    else:
                        p_w = p_w.split('*')[0]
                        if w_i + p_w_i >= len(text_words) or p_w != text_words[w_i + p_w_i][:len(p_w)]:
                            flag = False
                            break
                if flag:
                    dict_count += 1
    return dict_count

def count_sentences_in_text(words_list, text_sentences: list):
    dict_count = 0
    symbols = [",", ".", "!", "?"] 
    for sent in text_sentences:
        for symbol in symbols:
            sent = sent.replace(symbol, "").lower()
        sentence = [w.lower() for w in sent.split()]
        first_words_index_dict = find_first_word_index(phrases=words_list, sentence=sentence)
        for w in words_list:
            if phrase_in_sentence(phrase=w,  first_word_index=first_words_index_dict[w[0]], sentence=sentence):
                dict_count += 1
                break
    return dict_count


class RussiaCounter_ExactWord:
    def __init__(self):
        """
        whole words, whole sentences, three dicts
        """
        self.dummy_dict = ["russia", "ukraine", "war", "russian", "ukrainian"]
        self.words_freq_dict = {}
        rus_list = list(pd.read_excel("rus_dict_exact.xlsx", engine="openpyxl", header=None)[0])
        rus_name_list = list(pd.read_excel("rus_names.xlsx", engine="openpyxl", header=None)[1])
        rus_list = [w.strip().lower().split() if not w.isupper() else w.strip().split() for w in rus_list]
        rus_name_list = [w.strip().lower().split() if not w.isupper() else w.strip().split() for w in rus_name_list]
        self.words_freq_dict["rus_name"] = rus_name_list
        self.words_freq_dict["rus"] = rus_list

    def summary_one_dict(self, dict_name, text_words: list, text_sentences: list):
        # dict
        if dict_name == "dummy":
            dummy_count = 0
            for w in self.dummy_dict:
                if w in text_words:
                    dummy_count += 1
            return 1 if dummy_count >= 2 else 0
        elif dict_name == "rus":
            word_dict = self.words_freq_dict["rus"]
        else:
            word_dict = self.words_freq_dict["rus_name"]
        # word
        word_count = count_words_in_text(words_list=word_dict, text_words=text_words)
        # sentence
        sent_count = count_sentences_in_text(words_list=word_dict, text_sentences=text_sentences)
        return word_count, sent_count

    def count_by_dict(self, text):
        text_sentences = cut_sentence(text)
        symbols = [",", ".", "!", "?"]  # ??????????????????
        for symbol in symbols:
            text = text.replace(symbol, "").lower()
        text_words = text.split()

        dummy_var = self.summary_one_dict(dict_name="dummy", text_words=text_words, text_sentences=text_sentences)
        rus_w_count, rus_s_count = self.summary_one_dict(dict_name="rus", text_words=text_words, text_sentences=text_sentences)
        rus_name_w_count, rus_name_s_count = self.summary_one_dict(dict_name="rus_name", text_words=text_words, text_sentences=text_sentences)

        return dummy_var, rus_w_count, rus_s_count, rus_name_w_count, rus_name_s_count, len(text_words), len(text_sentences)

class RussiaCounter_Lemma:
    def __init__(self):
        """
        whole words, whole sentences, three dicts
        """
        self.dummy_dict = ['russia', "russia's", 'russian', 'russians', "russian's", "russians'",
                           'ukraine', "ukraine's", 'ukrainian', 'ukrainians', "ukrainian's", "ukrainians'",
                           'war', 'wars']
        
        self.words_freq_dict = {}
        rus_list = list(pd.read_excel("rus_dict_lemma.xlsx", engine="openpyxl", header=None)[0])
        rus_name_list = list(pd.read_excel("rus_names.xlsx", engine="openpyxl", header=None)[1])
        rus_list = [w.strip().lower().split() if not w.isupper() else w.strip().split() for w in rus_list]
        rus_name_list = [w.strip().lower().split() if not w.isupper() else w.strip().split() for w in rus_name_list]
        self.words_freq_dict["rus_name"] = rus_name_list
        self.words_freq_dict["rus"] = rus_list
        
    def summary_one_dict(self, dict_name, text_words: list, text_sentences: list):
        # dict
        if dict_name == "dummy":
            dummy_count = 0
            for w in self.dummy_dict:
                if w in text_words:
                    dummy_count += 1
            return 1 if dummy_count >= 2 else 0
        elif dict_name == "rus":
            word_dict = self.words_freq_dict["rus"]
        else:
            word_dict = self.words_freq_dict["rus_name"]
        # word
        word_count = count_words_in_text(words_list=word_dict, text_words=text_words)
        # sentence
        sent_count = count_sentences_in_text(words_list=word_dict, text_sentences=text_sentences)
        return word_count, sent_count

    def count_by_dict(self, text):
        text_sentences = cut_sentence(text)
        symbols = [",", ".", "!", "?"]  # ??????????????????
        for symbol in symbols:
            text = text.replace(symbol, "").lower()
        text_words = text.split()

        dummy_var = self.summary_one_dict(dict_name="dummy", text_words=text_words, text_sentences=text_sentences)
        rus_w_count, rus_s_count = self.summary_one_dict(dict_name="rus", text_words=text_words, text_sentences=text_sentences)
        rus_name_w_count, rus_name_s_count = self.summary_one_dict(dict_name="rus_name", text_words=text_words, text_sentences=text_sentences)

        return dummy_var, rus_w_count, rus_s_count, rus_name_w_count, rus_name_s_count, len(text_words), len(text_sentences)

    