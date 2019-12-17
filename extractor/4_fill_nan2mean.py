import time as t
import pandas as pd

if __name__ == "__main__":

    df = pd.read_csv('/nipa/Space_pred/desc_concat_OutCSV_0923/desc_0923_without_Bins_merged.csv')
    keys = list(df.keys())
    keys.remove('Name')

    for key in keys:
        df[key] = df[key].fillna(float(df[key].mean()))

    df.to_csv('../../DAT_0923/desc_Terms_filled.csv', index=False)

    




