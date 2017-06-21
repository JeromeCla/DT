# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 17:34:30 2017

@author: i0A103166
"""
import sys
import pandas as pd
import statistics
import matplotlib.pyplot as plt
from matplotlib import gridspec

#==============================================================================
# Functions
#==============================================================================
def plot_positions(Data): # POSITIONS MAP

    fig = plt.figure()
    fig.clear()
    
    XPos_name = 'X'
    YPos_name = 'Y'
    Pos_units = 'mm'
    
    ax0 = fig.add_subplot(1,1,1)
    ax0.grid(color='#DDDDDD')
    ax0.plot(Data['TkEd_pCM_Regle_X'], Data['TkEd_pCM_Regle_Y'], color='#000055')
    ax0.set_title('Axis Position')
    ax0.set_xlabel(XPos_name + ' [' + Pos_units + ']')
    ax0.set_ylabel(YPos_name + ' [' + Pos_units + ']')
    
    fig.subplots_adjust(left=0.15, bottom=0.1, top=0.90, right=0.98)
    
    plt.show()
    return

def plot_signals(Data,exclude,echantillon,operation):    
    Data.drop(exclude,axis=1).plot(subplots=True,title='Echantillon: ' +str(echantillon)+ ' Operation: ' +str(operation)+ '')

def plot_statistics(Var,X,Y,DoPlotStatistics,filename): # STATISTICS CURVES
    fig = plt.figure()
    fig.clear()
        
    # get text labels
    Var_name = Var.columns[0]
    Var_units = ''
    XPos_name = 'X'
    YPos_name = 'Y'
    Pos_units = 'mm'
    T=Var.index.values*0.004
    fig.suptitle(filename, fontsize=20)
#    plt.title(filename,y=1.08)
    
    if DoPlotStatistics:
        
        # prepare grid space for subplots
        gs = gridspec.GridSpec(4, 2, width_ratios=[1.5, 1]) 
        
        # Plot 1 : direct signal
        ax1 = fig.add_subplot(gs[0])
        ax1.grid(color='#DDDDDD')
        ax1.set_title('Statistics on \"' + Var_name + '\" variable')
        ax1.plot(T,Var[Var_name],'b', label=Var_name + ' [' + Var_units + ']')
        ax1.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL')
        plt.setp([ax1.get_xticklabels() for a in fig.axes[:-1]], visible=False)
        
        # Plot 2 : Derivative signals
        ax2 = fig.add_subplot(gs[2], sharex=ax1)
        ax2.grid(color='#DDDDDD')
        ax2.plot(T,Var['dt_'+Var_name],color='#AA5500', label='1st Derivative [' + Var_units + '/s]')
        ax2.plot(T,Var['dt2_'+Var_name],color='#5500AA', label='2nd Derivative [' + Var_units + '/sÂ²]')
        ax2.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DERIVATIVES')
        plt.setp([ax2.get_xticklabels() for a in fig.axes[:-1]], visible=False)
        
        # Plot 3 : Location signals
        ax3 = fig.add_subplot(gs[4], sharex=ax1)
        ax3.grid(color='#DDDDDD')
        ax3.plot(T,Var[Var_name],color='#0000FF', alpha=0.3, label=Var_name + ' [' + Var_units + ']')
        ax3.plot(T,Var['med_'+ Var_name],color='#0055AA', label='Median [' + Var_units + ']')
        ax3.plot(T,Var['min_'+ Var_name],color='#00AA00', label='Minimum [' + Var_units + ']')
        ax3.plot(T,Var['max_'+ Var_name],color='#AA0000', label='Maximum [' + Var_units + ']')
        ax3.legend(bbox_to_anchor=(1, 0.5), loc=6, title='TRACKING')
        plt.setp([ax3.get_xticklabels() for a in fig.axes[:-1]], visible=False)
        
        # Plot 4 : Scattering signals
        ax4 = fig.add_subplot(gs[6], sharex=ax1)
        ax4.grid(color='#DDDDDD')
        ax4.plot(T,Var['var_med_'+ Var_name],color='#FF0000', label='Variance [(' + Var_units + ')Â²]')
        ax4.plot(T,Var['std_med_'+ Var_name],color='#CC00CC', label='Std Deviation [' + Var_units + ']')
        ax4.legend(bbox_to_anchor=(1, 0.5), loc=6, title='SCATTERING')
        
        ax4.set_xlabel('Relative time [s]')
    
    else:
        gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1]) 
        
        # Plot 1 : direct signal
        ax1 = fig.add_subplot(gs[0])
        ax1.grid(color='#DDDDDD')
#        ax1.set_title('Statistics on \"' + Var_name + '\" variable')
        ax1.plot(T,Var[Var_name],'b', label=Var_name + ' [' + Var_units + ']')
#        ax1.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL')
       
        ax1.set_ylabel(Var_name + ' [' + Var_units + ']')
        ax1.set_xlabel('Relative time [s]')
        
        
    ax5 = fig.add_subplot(1,3,3)
    ax5.grid(color='#DDDDDD')
    ax5.plot(X, Y, color='#000055')
    ax5.set_title('Axis Position')
    ax5.set_xlabel(XPos_name + ' [' + Pos_units + ']')
    ax5.set_ylabel(YPos_name + ' [' + Pos_units + ']')
    
    head_width_set = (((max(X)-min(X))/20)\
                      +((max(Y)-min(Y))/20))/2
    head_length_set = head_width_set*1.5
    # trace begining arrow
    arr_dir_X = (X[10] - X[0])/10
    arr_dir_Y = (Y[10] - Y[0])/10
    ax5.arrow(X[0], Y[0], arr_dir_X, arr_dir_Y, 
              head_width=head_width_set, head_length=head_length_set, 
              color='#00DD00', alpha=0.3)
    # trace ending arrow
    arr_dir_X = (X.iloc[-1] - X.iloc[-11])/10
    arr_dir_Y = (Y.iloc[-1] - Y.iloc[-11])/10
    ax5.arrow(X.iloc[-1], Y.iloc[-1], arr_dir_X, arr_dir_Y, 
              head_width=head_width_set, head_length=head_length_set, 
              color='#DD0000', alpha=0.3)

    # Make subplots close to each other and hide x ticks for all but bottom plot
    fig.subplots_adjust(hspace=0.05)
    fig.subplots_adjust(left=0.05, bottom=0.05, top=0.92, right=0.99)    
    plt.show()
    
    return

