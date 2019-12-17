import sys

CLASS_PATH = './classes'
sys.path.insert(0, CLASS_PATH)

import pandas as pd 
import numpy as np 
import pickle 
from sklearn.externals import joblib
from sklearn.metrics import confusion_matrix, accuracy_score, mean_squared_error
from collections import Counter

from xgboost import XGBClassifier
import os
import csv
import copy

class Experiment_Test:
    cAllCases = 10000000000
    cAccThd = 95.0
    	
    def __init__(self, mAccThd, mType):
        self.cAccThd = float(mAccThd)
        self.type = mType
    
    def overall_Res_Multi_Class(self, mRes):
        newRes = np.transpose(list(mRes.values()))
        newRes_ov = list()
        for nr in newRes:
            newRes_ov.append(np.round(np.average(nr)))    

        return np.array(newRes_ov)

    def weightedRMSE(self, my_test, mRes):
        weiLst = list(copy.deepcopy(mRes))
        cntLst = list()

        for w in weiLst:
            cntLst.append(1 / (weiLst.count(w) / float(len(weiLst))))

        rmse_acc = mean_squared_error(my_test, mRes, sample_weight=cntLst)

        return rmse_acc
        


    
    def writeAns(self, mCsv_path, mAns):
        with open(mCsv_path, 'w') as fw:
            header = ['DOY', 'kp_0h', 'kp_3h', 'kp_6h', 'kp_9h', 'kp_12h', 'kp_15h', 'kp_18h', 'kp_21h']
    
            wr = csv.writer(fw)
            wr.writerow(header)
        
            doy_idx = 0
            for n in range(len(mAns)):
                if not (n%8):
                    doy_idx = doy_idx+1
                    wrLst = list([doy_idx])
        
                wrLst.append(mAns[n])
        
                if len(wrLst) == 9:
                    wr.writerow(wrLst)
    
    
    def jobLoader(self, mJob_Name):
        clf = joblib.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../classifier_' + self.type + '/' + mJob_Name + '_classifier.pkl'))
        
        features = pickle.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../classifier_' + self.type + '/' + mJob_Name + '_feats.pkl'), 'rb'))
        return clf, features
 

