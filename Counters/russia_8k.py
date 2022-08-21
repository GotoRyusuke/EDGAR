import numpy as np
import pandas as pd
import os
from russia_counter_lemma import RussiaCounter
import time
from tqdm import tqdm


def file_list(path):
    f_list = os.listdir(path)
    if ".DS_Store" in f_list:
        f_list.remove(".DS_Store")
    return sorted(f_list)


class RussiaNum:
    def __init__(self, data_name):
        self.data_name = data_name
        self.panel_data_path = "./" + "summary_2022Q2_" + data_name + ".xlsx"
        self.panel_df = pd.read_excel(self.panel_data_path)
        
        # initialise the counter module
        self.russia_counter = RussiaCounter()
        # indicator
        self.indicators = ["rus+ukr+war_dummy", "rus_word_num", "rus_sent_num", "rus_name_word_num", "rus_name_sent_num",
                           "total_word_num", "total_sent_num"]
        
        self.item_name_list = []
        for col in self.panel_df.columns:
            if "adrs" in col:
                item_name = col.split("_")[0]
                self.item_name_list.append(item_name)
                for ind in self.indicators:
                    self.panel_df[item_name + "_" + ind] = np.nan

    def count(self):
        start_time = time.time()
        for i in tqdm(range(len(self.panel_df))):
            for item_name in self.item_name_list:
                if pd.isna(self.panel_df.loc[i, item_name + "_adrs"]):
                    continue
                item_path = "F:/EDGAR/2022Q2_extracted/" + self.panel_df.loc[i, item_name + "_adrs"]
                if not pd.isna(item_path) and os.path.exists(item_path):
                    with open(item_path, "r", encoding="gbk") as f:
                        text = f.read()
                    count_result = self.russia_counter.count_by_dict(text=text)
                    for count_i, count_num in enumerate(count_result):
                        self.panel_df.loc[i, item_name + "_" + self.indicators[count_i]] = count_num
        return self.panel_df


if __name__ == "__main__":
    # os.getcwd()
    russia_num = RussiaNum(data_name = '10-Q')
    new_panel_df = russia_num.count()
    new_panel_df.to_excel("F:/EDGAR/word_freq/new_summary_2022Q2_lemma/new_summary_2022Q2_" + russia_num.data_name + "(lemma).xlsx", index=False)
