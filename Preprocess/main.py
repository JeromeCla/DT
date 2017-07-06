"""
# -*- coding: utf-8 -*-
Created on Wed May 31 13:45:10 2017
There is a shift of 3 between the index of Labview and the one of python 
because of parameters # 21, 23, 24 that are not taken into account in this code
 
@author: i0A103166
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import savecsv as sc
import DoStatistics as ds
import plotSignals as ps
import posttreatment as pt
import CurvAbsTransform as cat


plt.close("all")

# Echantillon and regime to analyze
echantillon = str(input("Enter the echantillon : " ))
regime = str(input("Enter the regime : " ))

#==============================================================================
# Create CSV File that can be downsampled with all possible signals
#==============================================================================    
#BatchList = [12]
#
#Dir_input = "C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Usinage" +(echantillon)+ "\\"
#Dir_Output = "C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Usinage" +(echantillon)+ "\\"
#sc.createcsv(Dir_input,Dir_Output,BatchList)
#



#==============================================================================
# LOAD FILES AND TREATMENT :
#   1) Define Curve Type (intern, extern etc...)
#   2) Resample the data in function of the curve abscissa
#   3) Create statistics for all signals
#==============================================================================

DoReloadFile = True
DoPlotStatistics = True
AbscCurvRef = True
PlotAll = False


#Variable to get the statistics on and window size
VarStatPlot = 'MainGeom_AbsCurTot_mm'
WindowSize=150

# Size of batch to train in ML
batch = 100

#Variabel NOT to save
VarNoSave = ['Stra_Etat_TableActive',\
             'Stra_ModifCROV_Final']

VarSignalsFile= "C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Preprocess\\Variable2.txt"
VarSelect, VarStat = pt.get_Variable_to_Save(VarSignalsFile)

# Loop to load and plot the regime asked by the user
for l in range (0,len(echantillon)):
    for i in range (0,len(regime)):
    
        datadir = 'C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Usinage' +echantillon[l] 
        filename = '\\usinage_0' +('0' + echantillon[l] if int(echantillon[l]) < 10 else echantillon[l])+ '_regime_00' +regime[i]+ '.csv'
        
        writeHeader = True
        for k in range(0,3):                                                                                       
            if DoReloadFile:
                Data_load = sc.loadcsv(datadir,filename,VarSelect)
            if AbscCurvRef:
                Data_load = cat.getDataAbsCurv(Data_load,str_RegressionKind='nearest')
            if DoPlotStatistics:
                Data_load = pt.addSignals(regime,Data_load)
                Data = Data_load[np.int(k*(len(Data_load)/3)):np.int((k+1)*(len(Data_load)/3))]
                del Data_load
                Data_stat= ds.DoStatistics(Data[VarStat],WindowSize)
            
            
            #==============================================================================
            # EXECUTION : Plot results
            #==============================================================================
            if PlotAll == True:
                print('Plot results... ', end='')
                
                #Plot geometry of workpiece
                fig_geom=ps.plot_positions(Data)
                
                #Plot signals in VarSelect except signals in VarExclude 
                fig_signal=ps.plot_signals(Data,VarNoPlot,echantillon,regime[i])
                
                #Plot statistics of signal VarStatPlot
                sign=pt.get_signal_stat(Data,Data_stat,VarStatPlot)
                fig_stat=ps.plot_statistics(sign,Data['MainGeom_AbsCurTot_mm'],Data['TkEd_pCM_Regle_X'],Data['TkEd_pCM_Regle_Y'] \
                                   ,1,filename,AbscCurvRef)
                
                #Plot strategies
                if {'Stra_Etat_TableActive'}.issubset(Data.columns):
                    ps.plotStrat(regime,Data,fig_signal)
        
            # Concatenation of all interesting signals (signals + statistics)
            Data = pd.concat([Data.drop(VarNoSave,axis=1), Data_stat ],axis=1)  
            
            
            del Data_stat
            sc.tocsv_ML(Data,datadir,filename,writeHeader)         
            del Data
            writeHeader = False



##==============================================================================
## EXECUTION : Treatment for Machine Learning algorithm 
##==============================================================================
#datadir = 'C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Usinage7\\usinage_007_regime_001_ML.csv' 
#print ("Loading ...")
#with open(datadir, mode='r', encoding='utf-8') as csvfile:
#    csvdata = pd.read_csv(csvfile, sep=';', dtype=str,header=0 ,skiprows=120000 ,nrows=100000 )
#Set_total = csvdata.apply(pd.to_numeric) 
#
#Set_total = Set_total.replace([np.inf, -np.inf], np.nan)    
#Set_total=Set_total.dropna(axis=1, how='all')
#Set_total=Set_total.dropna(axis=0, how='any')
#
#print ("Loaded")
#Training_Set = np.zeros((len(Set_total)/batch,10400))
#for i in range (0,len(Set_total),batch):
#    Training_Set[np.uint(i/batch)]=Set_total.as_matrix()[i:i+batch].flatten()
#    print(i)
#
#
#
#print ("Training ...")
## Training the set
#Model = KMeans(n_clusters = 2 ).fit(Training_Set)
#print ("Trained")
###################################  TEST  #####################################
#
#datadir = 'C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Usinage6\\usinage_006_regime_001_ML.csv' 
#
#with open(datadir, mode='r', encoding='utf-8') as csvfile:
#    csvdata = pd.read_csv(csvfile, sep=';', dtype=str,header=0,skiprows=120000  ,nrows=100000 )
#Set_total = csvdata.apply(pd.to_numeric) 
#print ("Loaded")
#
#Set_total = Set_total.replace([np.inf, -np.inf], np.nan)    
#Set_total=Set_total.dropna(axis=1, how='all')
#Set_total=Set_total.dropna(axis=0, how='any')
#
#Test_Set = np.zeros((len(Set_total)/batch,10400))
#for i in range (0,len(Set_total),batch):
#    Test_Set[np.uint(i/batch)]=Set_total.as_matrix()[i:i+batch].flatten()
#    print(i)
#    
##Testing the set
#print ("Testing ...")
#Prediction = Model.predict(Test_Set)
#
#print ("Tested")


#for i in VarSelect :
#    print(i)
#    csvdata = pd.read_csv("C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Usinage8\\usinage_008_regime_001_ML.csv", sep=';', dtype=str,usecols = [i])
#    csvdata2 = pd.read_csv("C:\\Users\\i0A103166\\Documents\\Python\\MachineLearning\\Usinage8\\usinage_008_regime_001_ML_nearest.csv", sep=';', dtype=str,usecols = [i])
#    if (csvdata2.all() != csvdata.all())[i]:
#        print("ERROR" +i+ "!!!!")
        
        