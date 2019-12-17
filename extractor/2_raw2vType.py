import sys
import pandas as pd
import numpy as np
import os
import time as t
import copy
import csv


if __name__=="__main__":
    dat_path = "../../Space_DAT/preprocessed_terms/concat_pp/"
    solar_files = os.listdir("../../Space_DAT/preprocessed_terms/concat_pp/")
    ans_file = "../../Space_DAT/Disturbance.csv"

    ans = pd.read_csv(ans_file, index_col=0)
    
    ansT = dict(ans.T)
    date = list(ansT.keys())
    yearCnt = list()
    doy = list()

    for d in date:
        yearCnt.append(d.split('-')[0])

    for yc in range(1999, 2014):
        for day in range(yearCnt.count(str(yc))):
            doy.append(str(yc) + "-" + str("%03d" % (day+1)))
        
    ans['doy'] = doy

    ans = pd.DataFrame(ans)
    ans.set_index('doy', inplace=True)
    ans = ans.T
    
    rowDat_init = dict()
    header = list(['Name', 'Label'])

    feats = ['Np', 'Tp', 'Vp', 'B_gsm_x', 'B_gsm_y', 'B_gsm_z', 'Bt']
    for feat in feats:
        for h in range(3):
            for m in range(60):
                header.append(feat + "_" + str(h) + "_" + str("%02d" % m))
                rowDat_init[h*100 + m] = -9999.9

    solar_files = list(solar_files)
    solar_files.sort()


    #for sFile in solar_files:
    if True:
        #sFile = 'concat_ace_2013.csv'    
        #sFile = 'concat_ace_2013.csv'    
        sFile = sys.argv[1]
        newDat = dict()
        print(sFile + " start!")
        print(dat_path + sFile)
        solar = dict(pd.read_csv(dat_path + sFile))

        leng = len(solar['year'])
        for feat in feats:
            rowDat = copy.deepcopy(rowDat_init) 
            for n in range(leng):
                rowDat[(int(solar['hr'][n]) % 3) * 100 + int(solar['min'][n])] = solar[feat][n]
                
                if not ((int(solar['hr'][n]) % 3) or (int(solar['min'][n]))): ## write timing
                    key = str(solar['year'][n]) + "_" + str("%03d" % solar['doy'][n]) + "_kp_" + str("%02d" % (int(solar['hr'][n]))) + "h"
                    if key not in newDat.keys():
                        try:
                            newDat[key] = list([ans[str(solar['year'][n]) + "-" + str("%03d" % solar['doy'][n])][int(solar['hr'][n]/3)]])
                        except:
                            newDat[key] = list([ans[str(solar['year'][n]-1) + "-" + str("%03d" % solar['doy'][n])][int(solar['hr'][n]/3)]])
                    newDat[key].extend(list(rowDat.values()))


        outPath = '../../Out_concat_CSV_0923/out_' + sFile
        with open(outPath, 'w') as csvWr:
            toCsv = csv.writer(csvWr) 
            toCsv.writerow(header)

            keys = list(newDat.keys())
            keys.sort()
            for key in keys:
                toCsv.writerow([key] + newDat[key])

            print(outPath)
            aFile = pd.read_csv(outPath)

            aFile['Name'] = (aFile['Name'].shift(periods=1).fillna(pd.NaT))
            aFile['Label'] = (aFile['Label'].shift(periods=1).fillna(pd.NaT))

            aLine = dict()

            for feat in feats:
                column_idx = list(['Name', 'Label']) 
                for h in range(3):
                    for m in range(60):
                        if feat not in aLine.keys():
                            aLine[feat] = list()
                    
                        aLine[feat].append(feat + "_" + str(h) + "_" + str("%02d" % m))

                        if (h==0) & (m==0):
                            aFile[feat + "_" + str(h) + "_" + str("%02d" % m)] = (aFile[feat + "_" + str(h) + "_" + str("%02d" % m)].shift(periods=1).fillna(-9999.9))

                column_idx.extend(aLine[feat])

                aFile_wr = copy.deepcopy(aFile)
                aFile_wr = aFile_wr.drop([0])

                print("Done! vType_" + feat)
                aFile_wr.to_csv('../../vTypes_concat_OutCSV_0923/' + str(sFile.split("_")[-1]).split(".")[0] + '/vType_' + feat + '_' + sFile, columns=column_idx, index=False)


