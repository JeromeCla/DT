# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# STATISTICAL MODULE
#------------------------------------------------------------------------------
# Description : Experiments of generic statistics calculations on a specified 
# signal.
# 
# +GF+ Machining Solutions, B.Lavazais 2017-06
#------------------------------------------------------------------------------

import sys
import pandas as pd
import statistics
import matplotlib.pyplot as plt
from matplotlib import gridspec
#==============================================================================
# Initializations
#==============================================================================


#VarSelect = 140 # td for pass 3
VarSelect = 174
VarXPos = 'TkEd_pCM_Regle_X'
VarYPos = 'TkEd_pCM_Regle_Y'

MovingWindow = 15  # number of samples for moving calculation


#if DoReloadFile:
#    # init data
#    X = pd.DataFrame() # Import raw data of selected variable (VarSelect) into X
#    XPos = pd.DataFrame() # X-axis positions
#    YPos = pd.DataFrame() # Y-axis positions
#    T = pd.DataFrame() # relatve time of samples
#    dT = pd.DataFrame() # delta time of samples
#    Path = pd.DataFrame() # cutting length path
#    # init statistics data
#    X_Vel = pd.DataFrame()
#    X_Acc = pd.DataFrame()
#    X_Med = pd.DataFrame()
#    X_SDev = pd.DataFrame()
#    X_Var = pd.DataFrame()
#    #X_Hrm = pd.DataFrame()
#    X_Min = pd.DataFrame()
#    X_Max = pd.DataFrame()


def DoStatistics(Data,MovingWindow):


    # CALUCULATE STATISTICS
    print('Process statistical signals... ', end='')
    
    # Calculate Velocity = X first derivative into X_Vel
    dt = Data.diff()
    cols = dt.columns[:]
    dt.rename(columns = dict(zip(cols, 'dt_' + cols)), inplace=True)       
    
    # Calculate Acceleration = X second derivative into X_Acc (=X_Vel first derivative)    
    dt2 = dt.diff()
    cols = dt2.columns[:]
    dt2.rename(columns = dict(zip(cols, 'dt2_' + cols)), inplace=True)    
    
    # Calculate X median from MovingWindow interval into X_Med
    med=Data.rolling(MovingWindow).median()
    cols = med.columns[:]
    med.rename(columns = dict(zip(cols, 'med_' + cols)), inplace=True)    
    
    # Calculate X standard_deviation from MovingWindow interval into X_Med    
    stand_dev=med.rolling(MovingWindow).std()
    cols = stand_dev.columns[:]
    stand_dev.rename(columns = dict(zip(cols, 'std_' + cols)), inplace=True)  
    
    # Calculate X variance from MovingWindow interval into X_Med
    variance=med.rolling(MovingWindow).var()
    cols = variance.columns[:]
    variance.rename(columns = dict(zip(cols, 'var_' + cols)), inplace=True)  
      
    # Calculate X minimum from the MovingWindow interval into X_Min
    min_data=Data.rolling(MovingWindow).min()
    cols = min_data.columns[:]
    min_data.rename(columns = dict(zip(cols, 'min_' + cols)), inplace=True)
    
    # Calculate X maximum from the MovingWindow interval into X_Max
    max_data=Data.rolling(MovingWindow).min()
    cols = max_data.columns[:]
    max_data.rename(columns = dict(zip(cols, 'max_' + cols)), inplace=True)  
    
    Data_stat = pd.concat([dt,dt2,med,stand_dev,variance,min_data,max_data],axis=1)
    
    print('Done !')
    
    return Data_stat



