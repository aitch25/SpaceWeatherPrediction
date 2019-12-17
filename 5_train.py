import sys
import copy
import math

import pandas as pd 
import numpy as np 
import pickle 
import sklearn.ensemble as ske 
from sklearn import tree, linear_model, preprocessing
from sklearn.feature_selection import SelectFromModel
from sklearn.externals import joblib
from sklearn.metrics import confusion_matrix, accuracy_score
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

import lightgbm as lgb

from imblearn.over_sampling import SMOTE, BorderlineSMOTE

from xgboost import XGBClassifier
import os
import csv
import json
import random as r
import time as t


CLASS_PATH = './classes'
sys.path.insert(0, CLASS_PATH)

class Experiment:
    cAllCases = 10000000000
    cAccThd = 95.0
    	
    def __init__(self, mAccThd):
        self.cAccThd = float(mAccThd)


    def jobStorage(self, mAlg, mJob_Name, mFeatures=None):
        print('Saving algorithm and feature list in classifier directory...')
        joblib.dump(mAlg, './classifier_Multi/' + mJob_Name + '_classifier.pkl')
        pickle.dump(mFeatures, open('./classifier_Multi/' + mJob_Name + '_feats.pkl', 'wb'))
        print('Saved')

    def weightedRMSE(self, my_test, mRes):
        weiLst = list(copy.deepcopy(mRes))
        cntLst = list()
        for w in weiLst:
            cntLst.append(weiLst.count(w) / float(sum(weiLst)))

        rmse_acc = mean_squared_error(my_test, mRes, sample_weight=cntLst)

        return rmse_acc



    def myWeightedRMSE(self, mAns, mSolved):
        lst1 = list(mAns)
        lst2 = list(mSolved)

        subLst = list()
        weiLst = list()

        for w in mAns:
            weiLst.append(w / sum(mAns))

        for w, l1, l2 in zip(weiLst, lst1, lst2):
            subLst.append(w * float(pow(l1-l2, 2)))

        return math.sqrt(sum(subLst))


    def sklearn_main(self, mCsv_path, mAlgo, mN_est, mLabType):
        data = pd.read_csv(mCsv_path, sep=',')

        data = data.dropna()
        del_count = []#['Np_count', 'Tp_count', 'Vp_count', 'Bt_count', 'B_gsm_x_count', 'B_gsm_y_count', 'B_gsm_z_count']


        for dk in data.keys():
            if 'Kp' in str(dk):
                del_count.append(dk)
            elif 'term' in str(dk):
                del_count.append(dk)
            

        y = data[mLabType].values

        try:
            data = data.drop(['Name', 'Label', 'Label_Bin'] + del_count, axis=1)
        except:
            data = data.drop(['Name', 'Label'] + del_count, axis=1)

        X = data.values
        
        algorithms = {
            "RandomForest": ske.RandomForestClassifier(n_estimators=mN_est, n_jobs=13), # Default 50
            "XGB": XGBClassifier(booster="gbtree", n_estimators=mN_est, nthread=13),
            "LGB": lgb.LGBMClassifier(n_jobs=13, objective='multiclass', random_state=100)
        }

        
        for n in range(self.cAllCases):
            oFeatures = list()
            fsel = ske.ExtraTreesClassifier().fit(X, y)
            oModel = SelectFromModel(fsel, prefit=True)
            
            X_new = oModel.transform(X)
            
            nb_features = X_new.shape[1]
            indices = np.argsort(fsel.feature_importances_)[::-1][:nb_features]

            for f in range(nb_features):
                print("%d. feature %s (%f)" % (f+1, data.columns[indices[f]], fsel.feature_importances_[indices[f]]))


            # XXX : take care of the feature order
            for f in sorted(np.argsort(fsel.feature_importances_)[::-1][:nb_features]):
                oFeatures.append(data.columns[f])
            
            

            #X_resampled, y_resampled = BorderlineSMOTE().fit_resample(X_train, y_train)
            #X_resampled, y_resampled = BorderlineSMOTE().fit_resample(X_new, y)

            X_resampled = X_new
            y_resampled = y
            X_train, X_test, y_train, y_test = train_test_split(X_resampled, 
                                                                    y_resampled, 
                                                                    test_size=0.2, 
                                                                    random_state=r.randrange(50))

            
            if mAlgo == "LGB":
                oClf = algorithms[mAlgo]
                opt_params = {'n_estimators':mN_est,
                                'boosting_type': 'dart',
                                #'objective': 'binary',
                                'objective': 'multiclass',
                                'num_leaves':2452,
                                'min_child_samples':212,
                                'reg_lambda':0.01}
                oClf.set_params(**opt_params)
                oClf.fit(X_train, y_train)

            else:
                oClf = algorithms[mAlgo]
                oClf.fit(X_train, y_train) # train
            
            res = oClf.predict(X_test)
            acc = (accuracy_score(y_test, res))*100
            mt = confusion_matrix(y_test, res)

            rmse_acc = mean_squared_error(y_test, res)
            wrmse_acc = exp.weightedRMSE(y_test, res)
            myWrmse_acc = exp.myWeightedRMSE(y_test, res)

            print("%d) %s : %f %%" % (n+1, mAlgo, acc))

            print("FP : ", (mt[0][1] / float(sum(mt[0]))) * 100 )
            print("FN : ", (mt[1][0] / float(sum(mt[1]))) * 100 )
            print("RMSE : ", rmse_acc)
            print("W-RMSE : ", wrmse_acc)
            print("my W-RMSE : ", myWrmse_acc)

            print("=======================================================================\n\n")

            if wrmse_acc <= self.cAccThd: 
                return wrmse_acc, oClf, oFeatures, res

if __name__=="__main__":
    try:
        csv_path = sys.argv[1]
        
    except:
        print("\n\n\nex 1) python3 run.py <csv file path> ")
        exit()
    
    
    exp = Experiment(1.0)

    accWeight = dict()
    resLst = list()

    weight_Df = pd.DataFrame()
    
    for n in range(7):
        acc_Alg1, rClf_Alg1, feat_Alg1, res_Alg1 = exp.sklearn_main(csv_path, "RandomForest", 300, 'Label')
        resLst.append(res_Alg1)
        exp.jobStorage(rClf_Alg1, "Alg1_" + str(n), feat_Alg1)
    
    for n in range(7):
        acc_Alg2, rClf_Alg2, feat_Alg2, res_Alg2 = exp.sklearn_main(csv_path, "XGB", 300, 'Label')
        resLst.append(res_Alg2)
        exp.jobStorage(rClf_Alg2, "Alg2_" + str(n), feat_Alg2)
    
    for n in range(7):
        acc_Alg3, rClf_Alg3, feat_Alg3, res_Alg3 = exp.sklearn_main(csv_path, "LGB", 300, 'Label')
        resLst.append(res_Alg3)
        exp.jobStorage(rClf_Alg3, "Alg3_" + str(n), feat_Alg3)
    

    overallRes = np.transpose(resLst)
    calcRes = list()
    for oRes in overallRes:
        calcRes.append(int(np.round(np.average(oRes))))



    print("=======================================================================\n\n")

 


