# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 14:24:14 2017

@author: s90786
"""

import os
#import csv
import pandas as pd
#import numpy as np
import sys
import statistics
import time
import datetime
#from time import sleep


### FOR TEST BENCH ONLY
#pCSVFilePath = 'data/usinage_004.csv'
#pInputPeriod = 0.004
#pOuputPeriod = 0.5

def DownsampleDataFrame(pDataFrame, pInputPeriod, pOuputPeriod, verbose):

    if verbose:
        print('- DownsampleList process started -')
    
    # intialize
    DSwindow = pOuputPeriod/pInputPeriod
    df_rows = len(pDataFrame)
    
    # check downsample window
    if DSwindow.is_integer() == False:
        sys.exit('ABORT : downsample window should be integer, check given sampling periods')
    else:
        DSwindow = int(DSwindow)
        if DSwindow > df_rows:
            sys.exit('ABORT : not enought sample to downsample at specified output period')
    
    # init values for loop
    df_beg = 0
    df_end = DSwindow
    out_row = 0
    rDownsampledData = pd.DataFrame()
    #Time = pd.DataFrame()
    
    while(1):
        
        if df_beg >= df_rows: # end of file reached (no data left to process)
            break
        else: # process data

            # display status
            if verbose:
                print (datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S - '), end='')            
                print('Process data rows [' + str(df_beg) + ':' + str(df_end) + '] ', end='')
                print('(' + str(int(((df_end)/df_rows)*100)) + '%)... ', end='')

            # calculate median values
            for var in range(0, len(pDataFrame.values[0])):
                rDownsampledData.loc[out_row,var] = statistics.median(pDataFrame.values[df_beg:df_end,var])

            if verbose:
                print('Done !')
            
            df_beg += DSwindow
            df_end += DSwindow
            if df_end > df_rows:
                df_end = df_rows
            out_row += 1
    
    # Update headers
    rDownsampledData.columns = pDataFrame.columns
    
    return rDownsampledData



def DownsampleFile(pCSVFilePath, pInputPeriod, pOuputPeriod):
    
    print('- DownsampleFile process started -')
    
    # intialize
    DSwindow = pOuputPeriod/pInputPeriod
    csv_rows = 0
    
    # check downsample window
    if DSwindow.is_integer() == False:
        sys.exit('ABORT : downsample window should be integer, check given sampling periods')
    else:
        DSwindow = int(DSwindow)
    
    # check file
    if os.path.isfile(pCSVFilePath) == False:
        sys.exit('ABORT : file \"' + pCSVFilePath + '\" does not exists')
         
    # read CSV header
    with open(pCSVFilePath, mode='r', encoding='utf-8') as csvfile:
        csvheader = pd.read_csv(csvfile, skiprows=0, nrows=0)
    
    print('CSV file \"' + pCSVFilePath + '\" has ' + str(len(csvheader.columns)) + ' variables')
    
    # get CSV total rows(lines)
    with open(pCSVFilePath, mode='r', encoding='utf-8') as csvfile:
        for csv_rows, l in enumerate(csvfile):
            pass
    
    # init values for loop
    csv_beg = 1
    out_row = 0
    DownsampledData = pd.DataFrame()
    #Time = pd.DataFrame()
    
    while(1):
        
        if csv_beg > csv_rows: # end of file reached (no data left to process)
            print('end of file')
            break
        else: # process data
            
            # display status
            print (datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S - '), end='')            
            print('import CSV data rows [' + str(csv_beg) + ':' + str(csv_beg+DSwindow) + '] ', end='')
            print('(' + str(int(((csv_beg+DSwindow)/csv_rows)*100)) + '%)... ', end='')
                            
            # import specific rows form csv file
            with open(pCSVFilePath, mode='r', encoding='utf-8') as csvfile:
                csvdata = pd.read_csv(csvfile, header=None, skiprows=csv_beg, nrows=DSwindow)
            
            print('Done !')
            
            if len(csvdata) == 0: # no data imported : no data left
                print('end of file')
                break
            else:
                print('\tMedian value calculation... ', end='')          
    
                # calculate median values
                for col in range(0, len(csvdata.values[0])):
                    DownsampledData.loc[out_row,col] = statistics.median(csvdata.loc[:,col])
                    if col == 0: # index column
                        DownsampledData.loc[out_row,col] *= pInputPeriod
        
    #            print('X_Med= ' + str(X_Med) + ' ', end='')
                print('Done !')
            
            csv_beg += DSwindow
            out_row += 1
    
    # Update headers
    DownsampledData.columns = csvheader.columns
    DownsampledData = DownsampledData.rename(columns={'Unnamed: 0':'time [s]'})
    
    # write data to file
    newfilename = pCSVFilePath[:-4] + '_downsample' + '{:.3f}'.format(pOuputPeriod) + 's.csv'
    
    print('Saving results in \"' + newfilename + '\"... ', end='')
    DownsampledData.to_csv(newfilename, sep=';', index=False)
    print('Done !')
    
    return
