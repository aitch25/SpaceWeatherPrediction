import os
import sys
import copy
import time as t
import numpy as np
import pandas as pd

if __name__=="__main__":
    fPath = "/nipa/Space_pred/vTypes_concat_OutCSV_0925/"
    dirs = list(os.listdir(fPath))
    dirs.sort()

    if True:
        dr = sys.argv[1]    
        merged_Df = pd.DataFrame()

        subDirs = os.listdir(fPath + dr)
        subDirs.sort()

        for f in subDirs:
            print(fPath + str(dr) + "/" + str(f))
            seq = str(f).split('Seq_')[-1]
            seq = int(seq.split('h')[0])

            dat = pd.read_csv(fPath + str(dr) + "/" + str(f).split('Seq_')[0] + 'Seq_' + str(seq) + 'h.csv')
            df = dat1.drop(['Label'], axis=1)


            name = dat['Name']
            label = dat['Label']
            newDf = pd.DataFrame()
            keys_inst_all = list()

            loop = df.shape[0]

            insDic = dict()
            hisDic = dict()
            keys = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']

            for l in range(loop):
                featLst = list()
                desc = pd.DataFrame(df.iloc[l])
                filtered = desc[desc > -9999]
                desc = filtered.describe()

                filt_value = list()
                for filt in filtered.values:
                    filt_value.extend(filt)

                filt_value = np.array(filt_value)
                filt_value = filt_value[~np.isnan(filt_value)]


                wrStr = ""
                wrStr = wrStr + name[l] + ","
                wrStr = wrStr + str(label[l])

                insDic['Name'] = name[l]
                insDic['Label'] = label[l]

                feat = f.replace("vType_", '')
                feat = feat.split("_terms")
                feat = feat[0]

                keys_inst = list()
                for key in keys:
                    keys_inst.append(feat + "_Seq_" + str(seq) + '_' + key)

                for k, d in zip(keys_inst, desc[l]):
                    insDic[k] = str(d)

                insDic.update(hisDic)
                newDf = newDf.append(insDic, ignore_index=True)
                newDf = newDf.reindex(columns=['Name', 'Label'] + keys_inst)


            if merged_Df.empty:
                merged_Df = newDf
           
            else:
                newDf = newDf.drop(['Label'], axis=1)
                merged_Df = merged_Df.join(newDf.set_index('Name'), on='Name')
                

            col_keys = list(merged_Df.keys())
            col_keys.remove('Name')
            col_keys.remove('Label')
            col_keys.sort()

            merged_Df = merged_Df.reindex(columns=['Name', 'Label'] + col_keys)
            merged_Df.to_csv('../../../desc_concat_OutCSV_0925/desc_0925_without_Bins_' + str(dr) + '.csv', index=False)


        

