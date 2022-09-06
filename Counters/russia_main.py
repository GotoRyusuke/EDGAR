import numpy as np
import pandas as pd
import os
from russia_counters import *
from tqdm import tqdm

class RussiaNum:
    def __init__(self, summary_file_name: str, store_path: str, mode: str):
        panel_df = pd.read_excel(summary_file_name)
        panel_df['f_date'] = [date.strftime('%Y-%m-%d')
                              if not isinstance(date, str)
                              else date
                              for date in panel_df['f_date']]
        self.panel_df = panel_df
        self.store_path = store_path
        
        # initialise the counter module
        if mode == 'lemma':
            self.russia_counter = RussiaCounter_Lemma()
        elif mode == 'exact word':
            self.russia_counter = RussiaCounter_ExactWord()
            
        # indicator
        self.indicators = ["rus+ukr+war_dummy",
                            "rus_word_num", "rus_sent_num", "rus_name_word_num", "rus_name_sent_num",
                           "total_word_num", "total_sent_num"]
        
        self.item_name_list = []
        for col in self.panel_df.columns:
            if "adrs" in col:
                item_name = col.split("_")[0]
                self.item_name_list.append(item_name)
                for ind in self.indicators:
                    self.panel_df[item_name + "_" + ind] = np.nan

    def count(self):
        for i in tqdm(range(len(self.panel_df)), ncols = 100):
            for item_name in self.item_name_list:
                if pd.isna(self.panel_df.loc[i, item_name + "_adrs"]):
                    continue
                item_path = self.store_path + '/' + self.panel_df.loc[i, item_name + "_adrs"]
                if not pd.isna(item_path) and os.path.exists(item_path):
                    with open(item_path, "r", encoding="gbk") as f:
                        text = f.read()
                    count_result = self.russia_counter.count_by_dict(text=text)
                    for count_i, count_num in enumerate(count_result):
                        self.panel_df.loc[i, item_name + "_" + self.indicators[count_i]] = count_num
        return self.panel_df