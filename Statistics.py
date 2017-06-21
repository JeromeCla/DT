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


if DoPlotStatistics:

    # CALUCULATE STATISTICS
    print('Process statistical signals... ', end='')
    
    # Calculate Velocity = X first derivative into X_Vel
    for row in range(0,len(X.values)):
        if row == 0:
            X_previous = X.values[row,0] # get initial value
            X_Vel.loc[row,0] = float(0) # set first output value to zero
        else:
            X_Vel.loc[row,0] = float((X.values[row]-X_previous)/dT.values[row])
            X_previous = X.values[row,0] # update previous value
    
    # Calculate Acceleration = X second derivative into X_Acc (=X_Vel first derivative)    
    for row in range(0,len(X_Vel.values)):
        if row == 0:
            X_previous = X_Vel.values[row,0] # get initial value
            X_Acc.loc[row,0] = float(0) # set first output value to zero
        else:
            X_Acc.loc[row,0] = float((X_Vel.values[row]-X_previous)/dT.values[row])
            X_previous = X_Vel.values[row,0] # update previous value
    
    # Calculate X median from MovingWindow interval into X_Med
    for row in range(MovingWindow-1,len(X.values)):
        if row == MovingWindow-1:
            for offset in range(0,MovingWindow):
                X_Med.loc[offset,0] = statistics.median(X.values[0:MovingWindow,0])
        else:
            X_Med.loc[row,0] = statistics.median(X.values[(row-(MovingWindow-1)):row+1,0])
    
    # Calculate X standard deviation from MovingWindow interval into X_Med
    for row in range(MovingWindow-1,len(X.values)):
        if row == MovingWindow-1:
            for offset in range(0,MovingWindow):
                X_SDev.loc[offset,0] = statistics.stdev(X.values[0:MovingWindow,0])
        else:
            X_SDev.loc[row,0] = statistics.stdev(X.values[(row-(MovingWindow-1)):row+1,0])
    
    # Calculate X variance from MovingWindow interval into X_Med
    for row in range(MovingWindow-1,len(X.values)):
        if row == MovingWindow-1:
            for offset in range(0,MovingWindow):
                X_Var.loc[offset,0] = statistics.variance(X.values[0:MovingWindow,0])
        else:
            X_Var.loc[row,0] = statistics.variance(X.values[(row-(MovingWindow-1)):row+1,0])
    
    # Calculate X harmonic mean from MovingWindow interval into X_Med
    #for row in range(MovingWindow-1,len(X)):
    #    if row == MovingWindow-1:
    #        for offset in range(0,MovingWindow):
    #            X_Hrm.append(statistics.harmonic_mean(X[0:MovingWindow]))
    #    else:
    #        X_Hrm.append(statistics.harmonic_mean(X[(row-(MovingWindow-1)):row+1]))
    
    # Calculate X minimum from the MovingWindow interval into X_Min
    for row in range(MovingWindow-1,len(X.values)):
        if row == MovingWindow-1:
            for offset in range(0,MovingWindow):
                X_Min.loc[offset,0] = min(X.values[0:MovingWindow,0])
        else:
            X_Min.loc[row,0] = min(X.values[(row-(MovingWindow-1)):row+1,0])
    
    # Calculate X maximum from the MovingWindow interval into X_Max
    for row in range(MovingWindow-1,len(X.values)):
        if row == MovingWindow-1:
            for offset in range(0,MovingWindow):
                X_Max.loc[offset,0] = max(X.values[0:MovingWindow,0])
        else:
            X_Max.loc[row,0] = max(X.values[(row-(MovingWindow-1)):row+1,0])
    
    print('Done !')
    



