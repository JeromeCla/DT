# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# STATISTICAL MODULE
#------------------------------------------------------------------------------
# Description : Experiments of generic statistics calculations on a specified 
# signal.
# 
# +GF+ Machining Solutions, B.Lavazais 2017-06
#------------------------------------------------------------------------------

#import os
import sys
#import csv
#import time
#import calendar
import pandas as pd
#import math
import statistics

import matplotlib.pyplot as plt
from matplotlib import gridspec
#import numpy as np

#==============================================================================
# Initializations
#==============================================================================

# FILES 
#datadir = '2 - Downsampled/' # data folder
datadir = '1 - Preprocessed/' # data folder

#filename = 'usinage_006_regime_003_DS.csv'
filename = 'usinage_006_regime_003.csv'
DoReloadFile = True
DoPlotStatistics = False

#VarSelect = 140 # td for pass 3
VarSelect = 174
#VarXPos = 'TkEd_pCM_Consi_Pos_X'
#VarYPos = 'TkEd_pCM_Consi_Pos_Y'
VarXPos = 'TkEd_pCM_Regle_X'
VarYPos = 'TkEd_pCM_Regle_Y'

MovingWindow = 15  # number of samples for moving calculation


if DoReloadFile:
    # init data
    X = pd.DataFrame() # Import raw data of selected variable (VarSelect) into X
    XPos = pd.DataFrame() # X-axis positions
    YPos = pd.DataFrame() # Y-axis positions
    T = pd.DataFrame() # relatve time of samples
    dT = pd.DataFrame() # delta time of samples
    Path = pd.DataFrame() # cutting length path
    # init statistics data
    X_Vel = pd.DataFrame()
    X_Acc = pd.DataFrame()
    X_Med = pd.DataFrame()
    X_SDev = pd.DataFrame()
    X_Var = pd.DataFrame()
    #X_Hrm = pd.DataFrame()
    X_Min = pd.DataFrame()
    X_Max = pd.DataFrame()


#==============================================================================
# Functions
#==============================================================================
def plot_positions(dummyfile): # POSITIONS MAP

    fig = plt.figure(2)
    fig.clear()
    
    if dummyfile == 1:
        # get text labels
        XPos_name = csvdata.columns[14]
        YPos_name = csvdata.columns[15]
        Pos_units = csvdata.values[1,15]
    else:
        XPos_name = VarXPos
        YPos_name = VarYPos
        Pos_units = ''
    
    ax0 = fig.add_subplot(1,1,1)
    ax0.grid(color='#DDDDDD')
    ax0.plot(XPos, YPos, color='#000055')
    ax0.set_title('Axis Position')
    ax0.set_xlabel(XPos_name + ' [' + Pos_units + ']')
    ax0.set_ylabel(YPos_name + ' [' + Pos_units + ']')
    ax0.set_aspect('equal')
    
    fig.subplots_adjust(left=0.15, bottom=0.1, top=0.90, right=0.98)
    
    plt.show()
    return


def plot_statistics(): # STATISTICS CURVES

    fig = plt.figure(1)
    fig.clear()
        
    # get text labels
    Var_name = csvdata.columns[VarSelect]
    Var_units = ''
    XPos_name = VarXPos
    YPos_name = VarYPos
    Pos_units = ''
    
    fig.suptitle(filename, fontsize=20)
#    plt.title(filename,y=1.08)
    
    if DoPlotStatistics:
        
        # prepare grid space for subplots
        gs = gridspec.GridSpec(4, 2, width_ratios=[1.5, 1]) 
        
        # Plot 1 : direct signal
        ax1 = fig.add_subplot(gs[0])
        ax1.grid(color='#DDDDDD')
        ax1.set_title('Statistics on \"' + Var_name + '\" variable')
        ax1.plot(T,X,'b', label=Var_name + ' [' + Var_units + ']')
        ax1.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL')
        plt.setp([ax1.get_xticklabels() for a in fig.axes[:-1]], visible=False)
        
        # Plot 2 : Derivative signals
        ax2 = fig.add_subplot(gs[2], sharex=ax1)
        ax2.grid(color='#DDDDDD')
        ax2.plot(T,X_Vel,color='#AA5500', label='Velocity [' + Var_units + '/s]')
        ax2.plot(T,X_Acc,color='#5500AA', label='Acceleration [' + Var_units + '/s²]')
        ax2.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DERIVATIVES')
        plt.setp([ax2.get_xticklabels() for a in fig.axes[:-1]], visible=False)
        
        # Plot 3 : Location signals
        ax3 = fig.add_subplot(gs[4], sharex=ax1)
        ax3.grid(color='#DDDDDD')
        ax3.plot(T,X,color='#0000FF', alpha=0.3, label=Var_name + ' [' + Var_units + ']')
        ax3.plot(T,X_Med,color='#0055AA', label='Median [' + Var_units + ']')
        ax3.plot(T,X_Min,color='#00AA00', label='Minimum [' + Var_units + ']')
        ax3.plot(T,X_Max,color='#AA0000', label='Maximum [' + Var_units + ']')
        ax3.legend(bbox_to_anchor=(1, 0.5), loc=6, title='TRACKING')
        plt.setp([ax3.get_xticklabels() for a in fig.axes[:-1]], visible=False)
        
        # Plot 4 : Scattering signals
        ax4 = fig.add_subplot(gs[6], sharex=ax1)
        ax4.grid(color='#DDDDDD')
        ax4.plot(T,X_Var,color='#FF0000', label='Variance [(' + Var_units + ')²]')
        ax4.plot(T,X_SDev,color='#CC00CC', label='Std Deviation [' + Var_units + ']')
        ax4.legend(bbox_to_anchor=(1, 0.5), loc=6, title='SCATTERING')
        
        ax4.set_xlabel('Relative time [s]')
    
    else:
        gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1]) 
        
        # Plot 1 : direct signal
        ax1 = fig.add_subplot(gs[0])
        ax1.grid(color='#DDDDDD')
#        ax1.set_title('Statistics on \"' + Var_name + '\" variable')
        ax1.plot(T,X,'b', label=Var_name + ' [' + Var_units + ']')
#        ax1.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL')
       
        ax1.set_ylabel(Var_name + ' [' + Var_units + ']')
        ax1.set_xlabel('Relative time [s]')
        
        
    ax5 = fig.add_subplot(1,3,3)
    ax5.grid(color='#DDDDDD')
    ax5.plot(XPos, YPos, color='#000055')
    ax5.set_title('Axis Position')
    ax5.set_xlabel(XPos_name + ' [' + Pos_units + ']')
    ax5.set_ylabel(YPos_name + ' [' + Pos_units + ']')
    ax5.set_aspect('equal')
    
    head_width_set = (((max(XPos.values[:,0])-min(XPos.values[:,0]))/20)\
                      +((max(YPos.values[:,0])-min(YPos.values[:,0]))/20))/2
    head_length_set = head_width_set*1.5
    # trace begining arrow
    arr_dir_X = (XPos.values[10,0] - XPos.values[0,0])/10
    arr_dir_Y = (YPos.values[10,0] - YPos.values[0,0])/10
    ax5.arrow(XPos.values[0,0], YPos.values[0,0], arr_dir_X, arr_dir_Y, 
              head_width=head_width_set, head_length=head_length_set, 
              color='#00DD00', alpha=0.3)
    # trace ending arrow
    arr_dir_X = (XPos.values[-1,0] - XPos.values[-11,0])/10
    arr_dir_Y = (YPos.values[-1,0] - YPos.values[-11,0])/10
    ax5.arrow(XPos.values[-1,0], YPos.values[-1,0], arr_dir_X, arr_dir_Y, 
              head_width=head_width_set, head_length=head_length_set, 
              color='#DD0000', alpha=0.3)

    # Make subplots close to each other and hide x ticks for all but bottom plot
    fig.subplots_adjust(hspace=0.05)
    fig.subplots_adjust(left=0.05, bottom=0.05, top=0.92, right=0.99)    
    plt.show()
    
    return

#==============================================================================
# EXECUTION : Load File
#==============================================================================

if DoReloadFile:
    
    csvdata = pd.DataFrame()
       
    print('Loading data from \"' + filename + '\"... ', end='')
    
    # Open CSV file of a real data set
    with open(datadir + filename, mode='r', encoding='utf-8') as csvfile:
        csvdata = pd.read_csv(csvfile, sep=';', dtype=str, usecols=[VarSelect])

    try:
        XPos_col = csvdata.columns.get_loc(VarXPos)
    except ValueError:
        print('ABORT : X Position not found')
        sys.exit()
        
    try:
        YPos_col = csvdata.columns.get_loc(VarYPos)
    except ValueError:
        print('ABORT : Y Position not found')
        sys.exit()

    for row in range(0,len(csvdata.values)):
        X.loc[row,0] = float(csvdata.values[row,VarSelect])
        XPos.loc[row,0] = float(csvdata.values[row,XPos_col])
        YPos.loc[row,0] = float(csvdata.values[row,YPos_col])
        if row == 0: # set initial value and time offset
            T_intial = float(csvdata.values[row,0])
            T_previous = T_intial
            dT.loc[row,0] = float(0)
            T.loc[row,0] = float(0)
        else:
            T_current = float(csvdata.values[row,0])
            dT.loc[row,0] = float(T_current-T_previous)
            T.loc[row,0] = float(T_current-T_intial)
            T_previous = T_current
    
    print('Done !')
         
    # check moving window length
    if MovingWindow > (len(X.values)):
        sys.exit('ABORT : MovingWindow value is too big')
else:
    # extract only data for variable
    for row in range(0,len(csvdata.values)):
        X.loc[row,0] = float(csvdata.values[row,VarSelect])


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
    

#==============================================================================
# EXECUTION : Plot results
#==============================================================================

print('Plot results... ', end='')

#plot_positions()
plot_statistics()

print('Done !')

