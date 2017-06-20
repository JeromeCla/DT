# -*- coding: utf-8 -*-
"""
Created on Wed May 31 13:45:10 2017
There is a shift of 3 between the index of Labview and the one of python 
because of parameters # 21, 23, 24 that are not taken into account in this code
 
@author: i0A103166
"""

import readbinary as rb
#import matplotlib.pyplot as plt
import savecsv as sc
import numpy as np
import math
#import pandas as pd
import posttreatment as pt
import datetime
import time
import sys

Dir_input = "../0 - Raw Data/"
Dir_Output = "../1 - Preprocessed/"

BatchList = [4,5,6,7,8,9,10,11]
#BatchList = [4]

SamplesPacket = 10*105
SamplingPeriod = 0.004
nb_variables = 235
#DownsampleWindow = 0

for N in range(0,len(BatchList)):
    
    for ds_group in range(0,2):
        
        if ds_group == 0:
            DownsampleWindow = 0
        else:
            DownsampleWindow = 105

        Filename_Input = Dir_input + "_dataint32_" + "%03.0f" % BatchList[N] +  ".bin"
        
        IndexLength = rb.fileIndexLength(Filename_Input, nb_variables) # process all file
        #IndexLength = 52 # process first 1000 lines
        
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
            
            Data.insert(0,np.linspace(index_start*SamplingPeriod, (index_end-1)*SamplingPeriod, (index_end-index_start)))
            
            Operation = pt.defineOperation(Regime)
            NewOperation = pt.currentOperation(Regime,0)  
        
            # set filename for display
            Filename_Ouput = "usinage_" + "%03.0f" % BatchList[N]
            Filename_Ouput += "_regime_" + "%03.0f" % NewOperation 
            if DownsampleWindow > 0:
                Filename_Ouput += "(ds)" 
            Filename_Ouput += ".csv"
            
            if NewOperation != CurOperation:
                # new regime detected
                if NewOperation > CurOperation:
                    # new file required
                    include_header = 1
                    print('New file created \"' + Filename_Ouput + '\"', end='')
                else:
                    # append to existing file
                    include_header = 0
                    print('Append back to file \"' + Filename_Ouput + '\"', end='')
                CurOperation = NewOperation
            else:
                # append to same file, no message
                include_header = 0
                
            # set filename for data saving
            Filename_Ouput = Dir_Output + "usinage_" + "%03.0f" % BatchList[N]
            Filename_Ouput += "_regime_" + "%03.0f" % CurOperation 
            if DownsampleWindow > 0:
                Filename_Ouput += "_DS" 
            Filename_Ouput += ".csv"
                
            
        #    print('operation = ' + str(CurOperation))
        
        #    if FirstPacket:
        #        include_header = 1
        #        FirstPacket = False
        #        print('New file created \"' + Filename_Ouput + '\"')
        #    else:
        #        include_header = 0
        #        print('')
            
            DataFrame = sc.tocsv(Data, Operation, Regime, parameters, BatchList[N], Filename_Ouput, include_header, DownsampleWindow)
        #    print(BatchList[N])
            print('')

