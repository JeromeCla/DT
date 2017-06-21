# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 15:45:23 2017

@author: i0A103166
"""
import numpy as np 
import pandas as pd

def defineOperation(Regime):
    # Regime 1 = MUT == 3 AND MUS == 7
    # Regime 2 = MUT == 3 AND MUS == 48
    # Regime 3 = MUT == 3 AND MUS == 67
    operation = np.uint(1) * np.logical_and(Regime[0]==3, Regime[1]==7)
    operation = operation + np.uint(2) * np.logical_and(Regime[0]==3, Regime[1]==48)    
    operation = operation + np.uint(3) * np.logical_and(Regime[0]==3, Regime[1]==67)
        
    return operation

def currentOperation(Regime, Index):
    # Regime 1 = MUT == 3 AND MUS == 7
    # Regime 2 = MUT == 3 AND MUS == 48
    # Regime 3 = MUT == 3 AND MUS == 67
    operation = np.uint(1) * np.logical_and(Regime[0,Index]==3, Regime[1,Index]==7)
    operation = operation + np.uint(2) * np.logical_and(Regime[0,Index]==3, Regime[1,Index]==48)
    operation = operation + np.uint(3) * np.logical_and(Regime[0,Index]==3, Regime[1,Index]==67)
    
    return operation


def Generate_CurveType(NumRegime, ArraySVM, ArrayET, ArrayCROV):
    # Generate value indicating geometric curve type:
    # 0 - Straight line
    # 1 - Internal curve
    # 2 - External curve
    #
    # input signals :
    # NumRegime = 1 for rought cut ; 2 = 2nd pass ; 3 = finishing (3rd pass)
    # ArraySVM = Array of values containing axis velocity override for pass 1 : Main_StratVitMax
    # ArrayET = Array of bitwise values containing strategic configuration override for pass 2 : Strat_Etat_TableActive
    # ArrayCROV = Array of values containing strategic curve override for pass 3 : Strat_ModifCROV_Final

    # to silent warning from NumPy
    np.seterr(all="ignore")
    
    if NumRegime == 1:
        # internal if ArraySVM < 1 ; external if ArraySVM > 1 ; straight else
        CurveType = np.uint(1) * np.less(ArraySVM[0],1.0) + np.uint(2) * np.greater(ArraySVM[0],1.0)
    elif NumRegime == 2:
        # internal if ArrayET bit 7 is 1 ; external if ArrayET bit 8 is 1 ; straight else
        CurveType = np.uint(1) * (np.round(np.divide(ArrayET[0]))==7) + np.uint(2) * (np.round(np.divide(ArrayET[0]))==8) 
    elif NumRegime == 3:
         # internal if ArrayET < 1 ; external if ArrayET > 1 ; straight else
        CurveType = np.uint(1) * np.less(ArrayCROV[0],1.0) + np.uint(2) * np.greater(ArrayCROV[0],1.0)
    else:
        # undefined : return NaN
        CurveType = np.nan * ArraySVM[0]
    
    return CurveType

def get_signal_stat(Data,Data_stat,VarName):
# Return the signal of a given signal and all its corresponding statistics

    sel_cols = [col for col in Data_stat.columns if VarName in col]
    sign=pd.concat([Data[VarName],Data_stat[sel_cols]],axis=1)

    return sign