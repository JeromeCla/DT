# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# STATISTICAL MODULE
#------------------------------------------------------------------------------
# Description : Experiments of generic statistics calculations on a specified 
# signal.
# 
# +GF+ Machining Solutions, B.Lavazais 2017-06
#------------------------------------------------------------------------------


import pandas as pd
import scipy
import scipy.stats
#==============================================================================
# Initializations
#==============================================================================


def DoStatistics(Time,Data,MovingWindow):


    # CALUCULATE STATISTICS
    print('Process statistical signals... ', end='')
    dTime = Time.diff()

    Data_stat = pd.DataFrame()
    
    # Calculate Velocity = X first derivative into X_Vel
    dt = pd.DataFrame()
    for k in Data.columns.values:
        dt[k] = Data[k].diff().div(dTime)
    cols = dt.columns[:]
    dt.rename(columns = dict(zip(cols, 'dt_' + cols)), inplace=True)       
    
    # Calculate Acceleration = X second derivative into X_Acc (=X_Vel first derivative)    
    dt2 = pd.DataFrame()
    for k in Data.columns.values:
        dt2[k] = (Data[k].diff().div(dTime)).diff().div(dTime)
    cols = dt2.columns[:]
    dt2.rename(columns = dict(zip(cols, 'dt2_' + cols)), inplace=True)    
    
    # Calculate X median from MovingWindow interval into X_Med
    med=Data.rolling(MovingWindow).median()
    cols = med.columns[:]
    med.rename(columns = dict(zip(cols, 'med_' + cols)), inplace=True)    
    
    # Calculate X standard_deviation from MovingWindow interval into X_Med    
    stand_dev=Data.rolling(MovingWindow).std()
    cols = stand_dev.columns[:]
    stand_dev.rename(columns = dict(zip(cols, 'std_' + cols)), inplace=True)  
    
    # Calculate X variance from MovingWindow interval into X_Med
    variance=Data.rolling(MovingWindow).var()
    cols = variance.columns[:]
    variance.rename(columns = dict(zip(cols, 'var_' + cols)), inplace=True)  
      
    # Calculate X minimum from the MovingWindow interval into X_Min
    min_data=Data.rolling(MovingWindow).min()
    cols = min_data.columns[:]
    min_data.rename(columns = dict(zip(cols, 'min_' + cols)), inplace=True)
    
    # Calculate X maximum from the MovingWindow interval into X_Max
    max_data=Data.rolling(MovingWindow).max()
    cols = max_data.columns[:]
    max_data.rename(columns = dict(zip(cols, 'max_' + cols)), inplace=True)  


    # Calculate moving Shannon's Entropy
    entropy = Data.rolling(window=MovingWindow, center=False).apply(scipy.stats.entropy)
    cols = entropy.columns[:]
    entropy.rename(columns = dict(zip(cols, 'etp_' + cols)), inplace=True) 
    
    Data_stat = pd.concat([dt,dt2,med,stand_dev,variance,min_data,max_data,entropy ],axis=1)
    
    print('Done !')
    
    return Data_stat



