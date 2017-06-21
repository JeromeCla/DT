# -*- coding: utf-8 -*-
"""
Created on Wed May 31 13:45:10 2017
There is a shift of 3 between the index of Labview and the one of python 
because of parameters # 21, 23, 24 that are not taken into account in this code
 
@author: i0A103166
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import savecsv as sc
import DoStatistics as ds
import plotSignals as ps
import posttreatment as pt

plt.close("all")

#==============================================================================
# LOAD FILES 
#==============================================================================

DoReloadFile = True
DoPlotStatistics = True

#Variable to get the statistics on and window size
VarStatPlot = 'MainGeom_AbsCurTot_mm'
WindowSize=150

#Variable to load from file
VarSelect= ['Gva_USA', 'MainGeom_AbsCurTot_mm',\
            'TkEd_pCM_Regle_X', 'TkEd_pCM_Regle_Y',\
            'Gva_VitParc5_Finale', 'TkEd_PI18_td', \
            'Main_PressionMesSup', 'Main_PressionMesInf',\
            'Stra_Etat_TableActive']

#Variable NOT to plot 
VarExclude= ['TkEd_pCM_Regle_X', 'TkEd_pCM_Regle_Y']

#Echantillon and regime to analyze
echantillon = input("Enter the echantillon : " )
regime = str(input("Enter the regime : " ))

#Loop to load and plot the regime asked by the user
for i in range (0,len(regime)):
    datadir = 'C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Usinage' +echantillon # 
    filename = '\\usinage_0' +('0' + echantillon if int(echantillon) < 10 else echantillon)+ '_regime_00' +regime[i]+ '.csv'
                                                                                    
    if DoReloadFile:
        Data = sc.loadcsv(datadir,filename,VarSelect)
        
    if DoPlotStatistics:
        Data_stat= ds.DoStatistics(Data,WindowSize)
    
    #==============================================================================
    # EXECUTION : Plot results
    #==============================================================================
    
    print('Plot results... ', end='')
    
    #Plot geometry of workpiece
    ps.plot_positions(Data)
    
    #Plot signals in VarSelect except signals in VarExclude 
    ps.plot_signals(Data,VarExclude,echantillon,regime[i])
    
    #Plot statistics of signal VarStatPlot
    sign=pt.get_signal_stat(Data,Data_stat,VarStatPlot)
    ps.plot_statistics(sign,Data['TkEd_pCM_Regle_X'],Data['TkEd_pCM_Regle_Y'] \
                       ,1,filename)


#==============================================================================
# Create CSV File that can be downsampled
#==============================================================================    

#Dir_input = "../0 - Raw Data/"
#Dir_Output = "../1 - Preprocessed/"
#sc.createcsv(Dir_input,Dir_Output):
