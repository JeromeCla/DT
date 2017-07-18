# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 11:26:33 2017

@author: i0A103166
"""

import numpy as np
import pandas as pd
import SignalProcessing as sp
import readbinary as rb
import math
import posttreatment as pt
import datetime
import time


def tocsv(Data, Operation, Regime, parameters, echantillon, target_file, include_header, downsample_window=-1):

    Data=np.insert(Data,0,Operation,axis=0)
    
    parameters=np.insert(parameters,0,'Operation')
    parameters=np.insert(parameters,1,'Time')

    datatosave = np.concatenate((np.transpose(Data),np.transpose(Regime)),axis=1)
    df_datatosave = pd.DataFrame(datatosave, columns = parameters)
    
    #Downsample
    if downsample_window > 0:
        df_datatosave = sp.DownsampleDataFrame(df_datatosave, 0.004, (0.004*downsample_window), False)
    
    if include_header:
        file_access = 'w'
    else:
        file_access = 'a'
        
    with open(target_file, file_access) as f:
        df_datatosave.to_csv(f, header=include_header, sep=';', index=False)
        
    return df_datatosave

def loadcsv(datadir,filename,VarSelect):
    
    csvdata = pd.DataFrame()
       
    print('Loading data from \"' + filename + '\"... ', end='')
    
    # Open CSV file of a real data set
    with open(datadir + filename, mode='r', encoding='utf-8') as csvfile:
        csvdata = pd.read_csv(csvfile, sep=';', dtype=str, usecols=VarSelect)

    print('Done !')
#    return csvdata.apply(pd.to_numeric) 
    return csvdata.astype(np.float)

def createcsv(Dir_root,BatchList):
#    Dir_input = "../0 - Raw Data/"
#    Dir_Output = "../1 - Preprocessed/"

    
    SamplesPacket = 10*105
    SamplingPeriod = 0.004
    nb_variables = 235
    #DownsampleWindow = 0
    
    for N in range(0,len(BatchList)):
    
        # set data files names
        Filename_Input = Dir_root + "Usinage" + str(BatchList[N]) + "\\_dataint32_" + "%03.0f" % BatchList[N] +  ".bin"
        Dir_Output = Dir_root + "Usinage" + str(BatchList[N]) + "\\"
                                                    
        IndexLength = rb.fileIndexLength(Filename_Input, nb_variables) # process all file
        
        PacketsToProcess = math.ceil(IndexLength/SamplesPacket)
        #FirstPacket = True
        CurOperation = -1
        NewOperation = 0
        
        for i in range(0, PacketsToProcess):
        #for i in range(0, 1):
            
            Data = []
            Regime = []
            parameters = []
            index_start = SamplesPacket*i
            index_end = SamplesPacket*(i+1)
            
            if index_end > IndexLength:
                index_end = IndexLength-1
            
            print (datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S - '), end='')
            Progress = float((i/PacketsToProcess)*100)
            print ('Processing batch %03d ' % BatchList[N], end = '')
            print ('Pass %03d ' % CurOperation, end = '')
            print ('(%.1f%%) ' % Progress, end = '')
            
        #    print('[' + str(index_start) + ':' + str(index_end) + '-' + str(index_end-index_start) + ']')
            
            Data, Regime, parameters = rb.readbinary(Filename_Input,index_start,index_end,nb_variables) 
            
            # add relative time offsets
            Data.insert(0,np.linspace(index_start*SamplingPeriod, (index_end-1)*SamplingPeriod, (index_end-index_start)))
 
            # Extract machining sequences
            Operation = pt.defineOperation(Regime)
    
            # Detect curve abscissa reset
            if i==0: # first packet
                # get index of curve abscissa
                CAindex, = np.where(parameters=='MainGeom_AbsCurTot_mm')[0]
            # find zeros
            CAreset, = np.where(Data[CAindex]==0)
            if CAreset.size > 0:
    
                NewOperation = pt.currentOperation(Regime,-1)
                
                if NewOperation != CurOperation:
    
                    # Firstly : append begining to existing file
                    if CAreset[0] > 0:
                        # append to existing file
                        include_header = 0
                        
                        # filename
                        Filename_Ouput = "usinage_" + "%03.0f" % BatchList[N]
                        Filename_Ouput += "_regime_" + "%03.0f" % CurOperation 
                        Filename_Ouput += ".csv"
                        
                        # save data to file
                        DataFrame = tocsv(\
                             [item[0:CAreset[0]] for item in Data], 
                             Operation[0:CAreset[0]], 
                             Regime.T[0:CAreset[0]].T,  
                             parameters, 
                             BatchList[N], 
                             Dir_Output+Filename_Ouput, 
                             include_header)
                    
                    # filename
                    Filename_Ouput = "usinage_" + "%03.0f" % BatchList[N]
                    Filename_Ouput += "_regime_" + "%03.0f" % NewOperation 
                    Filename_Ouput += ".csv"
                    
                    if NewOperation > CurOperation: # new regime detected
                        # new file required
                        include_header = 1
                        print('New file created \"' + Filename_Ouput + '\"', end='')
                        
                    else:
                        # append to existing file
                        include_header = 0
                        print('Append back to file \"' + Filename_Ouput + '\"', end='')
                        
                    # save data to file
                    DataFrame = tocsv(\
                         [item[CAreset[0]:] for item in Data], 
                         Operation[CAreset[0]:], 
                         Regime.T[CAreset[0]:].T,  
                         parameters, 
                         BatchList[N], 
                         Dir_Output+Filename_Ouput, 
                         include_header)
                        
                    CurOperation = NewOperation
                else:
                    # append aLL to same file, no message
                    include_header = 0
                    
                    # filename
                    Filename_Ouput = "usinage_" + "%03.0f" % BatchList[N]
                    Filename_Ouput += "_regime_" + "%03.0f" % CurOperation 
                    Filename_Ouput += ".csv"
                    
                    # save data to file
                    DataFrame = tocsv(\
                         Data, 
                         Operation, 
                         Regime,  
                         parameters, 
                         BatchList[N], 
                         Dir_Output+Filename_Ouput, 
                         include_header)
                    
            else:
                # append aLL to same file, no message
                include_header = 0
                
                # filename
                Filename_Ouput = "usinage_" + "%03.0f" % BatchList[N]
                Filename_Ouput += "_regime_" + "%03.0f" % CurOperation 
                Filename_Ouput += ".csv"
                
                # save data to file
                DataFrame = tocsv(\
                     Data, 
                     Operation, 
                     Regime,  
                     parameters, 
                     BatchList[N], 
                     Dir_Output+Filename_Ouput, 
                     include_header)
                
            print('')