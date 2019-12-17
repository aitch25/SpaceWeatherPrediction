import pandas as pd
import os
import time as t
import copy
import csv
from tqdm import tqdm
import sys


if __name__=="__main__":
    dat_path = "../../Space_DAT/Solar_wind_terms/"
    solar_files = os.listdir("../../Space_DAT/Solar_wind_terms/")

    times = ['year', 'doy', 'hr', 'min']
    feats = ['Np', 'Tp', 'Vp', 'B_gsm_x', 'B_gsm_y', 'B_gsm_z', 'Bt']

    overallDic = dict()
    overallPd = list()
            
    sFile = sys.argv[1]
    print(sFile + " srart!")
    dat = dict(pd.read_csv(dat_path + sFile))
    year = int(dat['year'][0])

    overallDic['key'] = list()
    for time in times: 
        overallDic[time] = list()
    for feat in feats: 
        overallDic[feat] = list()

    doy = list(dat['doy'])[-2]

    for d in range(doy):
        for h in range(24):
            for m in range(60):
                overallDic['year'].append(year)
                overallDic['doy'].append(d+1)
                overallDic['hr'].append(h)
                overallDic['min'].append(m)

                for feat in feats:
                    overallDic[feat].append(-9999.9)

    overallDic['year'].append(year+1)
    overallDic['doy'].append(1)
    overallDic['hr'].append(0)
    overallDic['min'].append(0)

    for feat in feats:
        overallDic[feat].append(-9999.9)

    for (y, d, h, m) in zip(overallDic['year'], overallDic['doy'], overallDic['hr'], overallDic['min']):
        overallDic['key'].append(str(y) + "-" + str(d) + "-" + str(h) + "-" + str(m))

    datLen = len(dat['doy'])
    for (n, y, d, h, m) in zip(range(datLen), dat['year'], dat['doy'], dat['hr'], tqdm(dat['min'])):
        idx = overallDic['key'].index((str(y) + "-" + str(d) + "-" + str(h) + "-" + str(m)))

        for feat in feats:
            overallDic[feat][idx] = dat[feat][n]
        
    allFeats = times + feats
    filledPd = pd.DataFrame(overallDic, columns=allFeats)

    print(filledPd.head) 
    filledPd.to_csv('../../Space_DAT/preprocessed_terms/terms_pproced_' + sFile.split('/')[-1], index=False)


