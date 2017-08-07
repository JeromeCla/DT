# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 10:35:26 2017

@author: i0A103166
"""

"""
# -*- coding: utf-8 -*-
Created on Wed May 31 13:45:10 2017
There is a shift of 3 between the index of Labview and the one of python 
because of parameters # 21, 23, 24 that are not taken into account in this code
 
@author: i0A103166
"""

import pandas as pd
import numpy as np
import savecsv as sc
import DoStatistics as ds
import posttreatment as pt
import CurvAbsTransform as cat



def createDataML(Dir_root,echantillon,regime,WindowSize):

    #Variabel NOT to save
    VarNoSave = ['Stra_Etat_TableActive','Stra_ModifCROV_Final']
    
    VarSignalsFile= Dir_root + "Preprocess\\Variable.txt"
    VarSelect, VarStat, VarInterpLin, VarInterpNearest = pt.get_Variable_to_Save(VarSignalsFile)
    
    #==============================================================================
    # LOAD FILES AND TREATMENT :
    #   1) Define Curve Type (intern, extern etc...)
    #   2) Resample the data in function of the curve abscissa
    #   3) Create statistics for all signals
    #==============================================================================
    
    # Loop to load through all the echnatillon and the regimes asked by the user
    for l in range (0,len(echantillon)):
        for i in range (0,len(regime)):
        
            datadir = Dir_root + "Usinage" + str(echantillon[l]) 
            filename = '\\usinage_0' +('0' + str(echantillon[l]) if int(echantillon[l]) < 10 else str(echantillon[l]))+ '_regime_00' +str(regime[i])+ '.csv'       
            writeHeader = True
            createNewFile = 'w'
            for k in range(0,3):                                                                                       
                Data_load = sc.loadcsv(datadir,filename,VarSelect)
                Data_load = cat.getDataAbsCurv(Data_load,VarInterpLin,VarInterpNearest)
                Data_load = pt.addSignals(regime[i],Data_load)
                Data = Data_load[np.int(k*(len(Data_load)/3)):np.int((k+1)*(len(Data_load)/3))]
                del Data_load
                Data_stat= ds.DoStatistics(Data['Time'],Data[VarStat],WindowSize)
            
                # Concatenation of all interesting signals (signals + statistics)
                Data = pd.concat([Data.drop(VarNoSave,axis=1), Data_stat ],axis=1)  
                            
                del Data_stat
                with open(datadir + filename[0:-4] + '_ML_nearest.csv', mode=createNewFile) as f:
                    Data.to_csv(f, header=writeHeader, sep=';', index=False)  
                del Data
                writeHeader = False
                createNewFile = 'a'
                
def loadDataML(Dir_root,echantillon,regime,VarSelect):
    datadir = Dir_root + "Usinage" + str(echantillon)
    filename = '\\usinage_0' +('0' + str(echantillon) if int(echantillon) < 10 else str(echantillon))+ '_regime_00' +str(regime)+ '.csv'       

    csvdata = pd.DataFrame()
    print('Loading data from \"' + filename[0:-4] + '_ML_nearest.csv\"... ', end='')    
    # Open CSV file of a real data set
    with open(datadir + filename[0:-4] + '_ML_nearest.csv', mode='r', encoding='utf-8') as csvfile:
        csvdata = pd.read_csv(csvfile, sep=';', dtype=str, usecols=VarSelect)
    print('Done !')
    
    return csvdata.astype(np.float)