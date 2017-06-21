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
#==============================================================================
# LOAD FILES 
#==============================================================================

echantillon= 6
operation = 3

datadir = 'C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Usinage6' # 
filename = '\\usinage_006_regime_003.csv'

DoReloadFile = True
DoPlotStatistics = True
VarStatPlot = 'Gva_VitParc5_Finale'

VarSelect= ['Gva_USA', 'MainGeom_AbsCurTot_mm',\
            'TkEd_pCM_Regle_X', 'TkEd_pCM_Regle_Y',\
            'Gva_VitParc5_Finale', 'TkEd_PI18_td', \
            'Main_PressionMesSup', 'Main_PressionMesInf',\
            'Stra_Etat_TableActive']

VarExclude= ['TkEd_pCM_Regle_X', 'TkEd_pCM_Regle_Y']

if DoReloadFile:
    Data = sc.loadcsv(datadir,filename,VarSelect)
    Data=Data.apply(pd.to_numeric)
    
if DoPlotStatistics:
    Data_stat= ds.DoStatistics(Data,50)

#==============================================================================
# EXECUTION : Plot results
#==============================================================================

print('Plot results... ', end='')

ps.plot_positions(Data)
ps.plot_signals(Data,VarExclude,echantillon,operation)

sign=pt.get_signal_stat(Data,)
ps.plot_statistics(sign,Data['TkEd_pCM_Regle_X'],Data['TkEd_pCM_Regle_Y'] \
                   ,1,filename)

#print('Done !')


#==============================================================================
# Create CSV File that can be downsampled
#==============================================================================    

#Dir_input = "../0 - Raw Data/"
#Dir_Output = "../1 - Preprocessed/"
#sc.createcsv(Dir_input,Dir_Output):
