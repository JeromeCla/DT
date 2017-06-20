# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 11:26:33 2017

@author: i0A103166
"""

import numpy as np
import pandas as pd
import SignalProcessing as sp

def tocsv(Data, Operation, Regime, parameters, echantillon, target_file, include_header, downsample_window):

    Data=np.insert(Data,1,Operation,axis=0)
    
    parameters=np.insert(parameters,0,'Operation')
    parameters=np.insert(parameters,0,'Time')

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