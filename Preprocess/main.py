"""
# -*- coding: utf-8 -*-
Created on Wed May 31 13:45:10 2017
There is a shift of 3 between the index of Labview and the one of python 
because of parameters # 21, 23, 24 that are not taken into account in this code
 
@author: i0A103166
"""

import createData as cd
import matplotlib.pyplot as plt
import plotSignals as ps

plt.close("all")
# Select the root directory from where we will reach the data
# (i.e Variable.txt and binary files)
Dir_root = "C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\"

#Select what actions you wan tot do :
PlotAll = True
saveCSV = False
loadData = True

#Variable to get the statistics on and window size
VarStatPlot = 'Main_USA'
VarStat=[VarStatPlot, 'dt_'+VarStatPlot,'dt2_'+VarStatPlot,'max_'+VarStatPlot,'min_'+VarStatPlot,'std_'+VarStatPlot,'med_'+VarStatPlot,'var_'+VarStatPlot]

VarSelect = ['Time','Main_USA','MainGeom_AbsCurTot_mm','Main_PressionStr','Main_PressionMesSup','Rewindings','CurveType','TkEd_pCM_Regle_X','TkEd_pCM_Regle_Y']
VarPlot = ['Main_USA','MainGeom_AbsCurTot_mm','Main_PressionStr','Main_PressionMesSup','Rewindings']

WindowSize = 150

# Echantillon and regime to analyze. Specify only one echantillon for plotting 
# (multiple are only allowed for saving file)
echantillon = [int(x) for x in (input("Enter the echantillon separate by space : " ).split())]
regime = [int(x) for x in (input("Enter the regime separate by space : " ).split())]

if saveCSV == True:
    cd.createDataML(Dir_root,echantillon,regime,WindowSize, newRawData=False)
        
for i in range (0,len(regime)):    
    if loadData == True:
        Data = cd.loadDataML(Dir_root,echantillon[0],regime[i],VarSelect+VarStat)
    if PlotAll==True:
        ps.plotAll(Data,VarPlot,VarStat,echantillon,regime[i],refAbsCurv=True)
    
       
