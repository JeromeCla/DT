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


def Generate_CurveType(regime,Data):
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
    
    strat = Data['Stra_Etat_TableActive']
    strat_finition= Data['Stra_ModifCROV_Final']
    CurveType = np.zeros(len(Data))
    
    if regime != 3:
        CurveType[strat[(strat/10000).apply(np.fix)==7].index.values] = 7
        CurveType[strat[(strat/10000).apply(np.fix)==8].index.values] = 8
        CurveType[strat[(strat/10000).apply(np.fix)==5].index.values] = 5          
        CurveType[strat[(strat/10000).apply(np.fix)==6].index.values] = 6  
    if regime == 3:
        CurveType[strat_finition[strat_finition<1].index.values] = 7
        CurveType[strat_finition[strat_finition>1].index.values] = 8
    
    return CurveType

def addSignals(regime,Data):
    # We set the start time at zero
    Data['Time'] = Data['Time'] - Data['Time'][0]
    Data['CurveType'] = Generate_CurveType(regime,Data)
    return Data

def get_signal_stat(Data,VarName):
    # Return the signal of a given signal and all its corresponding statistics
    sel_cols = [col for col in Data.columns if VarName in col]
    return Data[sel_cols]

def get_Variable_to_Save(filename):
    with open(filename,'r') as fd:
        data = np.loadtxt(fd, delimiter=' ', dtype={'names': ('col1', 'col2', 'col3','col4','col5','col6'), 'formats': ('S30', 'f8', 'S1','S30','S30','S30')})
    VarStat = []
    VarSelect = ['Time']
    VarInterpLin = ['Time']
    VarInterpNearest = []
    
    for k in data:
        if k[4].astype(str) == 'StatYes':
            VarStat.append(k[0].astype(str))
        if k[3].astype(str) == 'MLYes':
            VarSelect.append(k[0].astype(str))
            if k[5].astype(str) == 'Interplin':
                VarInterpLin.append(k[0].astype(str))
            if k[5].astype(str) == 'Interpnearest':
                VarInterpNearest.append(k[0].astype(str))

    return VarSelect,VarStat,VarInterpLin,VarInterpNearest
