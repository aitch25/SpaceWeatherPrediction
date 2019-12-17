import sys

CLASS_PATH = './classes'
sys.path.insert(0, CLASS_PATH)

import pandas as pd 
import numpy as np 
import pickle 
import sklearn.ensemble as ske 
from sklearn.feature_selection import SelectFromModel
from sklearn.externals import joblib
from sklearn.metrics import confusion_matrix, accuracy_score, mean_squared_error
from xgboost import XGBClassifier
import os
import json
import time as t

import Experiment_Test as test

if __name__=="__main__":
    try:
        test_path = sys.argv[1]
        data = pd.read_csv(test_path, sep=',')
        y = data['Label'].values
        y_True = True
        print("True")

    except:
        test_path = sys.argv[1]
        data = pd.read_csv(test_path, sep=',')
        y_True = False
        print("False")

    
    exp = test.Experiment_Test(70., 'Multi')
    
    resDic = dict()
    resLst = list()
    
    for n in range(7):
        fClf, features = exp.jobLoader('Alg1_' + str(n))
        Xt = data[features].values
        res = fClf.predict(Xt)
        resLst.append(res)
        resDic['Alg1_' + str(n)] = res

        if y_True:
            acc = accuracy_score(y, res)*100
            print("\nAcc : ", acc)
            print("RMSE : ", mean_squared_error(y, res))
            print("W-RMSE : ", exp.weightedRMSE(y, res))
       
    for n in range(7):
        fClf, features = exp.jobLoader('Alg2_' + str(n))
        Xt = data[features].values
        res = fClf.predict(Xt)
        resLst.append(res)
        resDic['Alg2_' + str(n)] = res

        if y_True:
            acc = accuracy_score(y, res)*100
            print("\nAcc : ", acc)
            print("RMSE : ", mean_squared_error(y, res))
            print("W-RMSE : ", exp.weightedRMSE(y, res))
    	
    for n in range(7):
        fClf, features = exp.jobLoader('Alg3_' + str(n))
        Xt = data[features].values
        res = fClf.predict(Xt)
        resLst.append(res)
        resDic['Alg3_' + str(n)] = res

        if y_True:
            acc = accuracy_score(y, res)*100
            print("\nAcc : ", acc)
            print("RMSE : ", mean_squared_error(y, res))
            print("W-RMSE : ", exp.weightedRMSE(y, res))
    	

    overallRes = np.transpose(resLst)
    calcRes = list()
    for oRes in overallRes:
        calcRes.append(int(np.round(np.average(oRes))))


    if y_True:
        print("\n -> overall RMSE : ", mean_squared_error(y, calcRes))
        print(" -> overall W-RMSE : ", exp.weightedRMSE(y, calcRes))

    exp.writeAns('./solar_ans_0925_RF_comb.csv', calcRes)
    print("=======================================================================\n\n")

 

