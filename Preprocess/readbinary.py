# -*- coding: utf-8 -*-
"""
Created on Tue May 30 13:28:49 2017

@author: i0A103166
"""

import scipy.io
import numpy as np
#import math
import mmap
#import time
#import datetime
import os

# -------------------------------------------------fileIndexLength--------------------------------- 

def fileIndexLength(DataFileName, Nvars):
    
    # Get data file size in bytes
    statinfo = os.stat(DataFileName)
    bytesize = statinfo.st_size
    
    # Calculate index length eith number of variables
    return int(bytesize / Nvars / 4)


# -------------------------------------------------strfindfile--------------------------------- 
# Input : DataFileName=String of full path of the binary file .bin
#         SigName = String of the parameter to find
# Output : k = Position of the parameter's name in the .ini file

def strfindfile(DataFileName,SigName):
    k=[0,0]
    SigName = SigName + ' ' #The whitespace is necessary to search the exact variable     
    FileNameIni = DataFileName[0:-4] + ".ini"   
    with open(FileNameIni, 'r') as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
        b = bytearray()
        b.extend(SigName.encode())
        k[0]=s.find(b) 
        k[1]=s.find(b,k[0]+1) 
    return k

# -------------------------------------------------GetTraceFromFile--------------------------------- 
# Input : SigName = String of the parameter to find 
#         FileIniName = String of full path of the file .ini
#         DataFileName = String of full path of the binary file .bin
#         Nvars = 
#         idx_deb = index of first sample
#         idw__fin = index of last sample (value can be inf to be sure to get all the samples)
#         Signe = Whether this parameter is (un)signed          
# Output : Trace = Array of array representing a matrix MxN where M:Number of parameters
#                                                                 N: Number of samples
# Work : 

def GetTraceFromFile(SigName, FileIniNames, DataFileName, Nvars, idx_deb, idx_fin, Signe):
    
    UndefinedVal=int('cafecafe',16)

    if Signe == 'pp':   Signe='+'
    if Signe == 'p':   Signe='+'
    if Signe == 'm':   Signe='-'
    

    k=strfindfile(DataFileName,SigName)
    
    if not k:
        print ('La variable ' +SigName+ ' n''existe pas dans le fichier .ini')
    elif k[1]==-1:
        print ('Le gain de la variable ' +SigName+ ' n''est pas défini dans le fichier .ini')

    LenIniFile = len(FileIniNames);

# Exctract the parameter's number (i.e id)
    substr=FileIniNames[k[0]:min(k[0]+100,LenIniFile)]
    substr_st = ''.join([chr(item) for item in substr])
    eq=substr_st.find('=')
    cr=substr_st.find(';')
    list_char=[chr(i) for i in FileIniNames[k[0]+np.arange(eq+1,cr)]]
    list_char=''.join(list_char)
    VarNr=int(list_char)

# Extract the gain of the parameter if there is one
    if k[1] != -1:
        substr=FileIniNames[k[1]:min(k[1]+100,LenIniFile)]
        substr_st = ''.join([chr(item) for item in substr])
        eq=substr_st.find('=')
        cr=substr_st.find(';')
        list_char=[chr(i) for i in FileIniNames[k[1]+np.arange(eq+1,cr)]]
        list_char=''.join(list_char)
        VarGain=float(list_char)
    else: 
        VarGain=1

#Read the values and store them in Trace    
    fid=open(DataFileName, 'r');
    skip_deb=Nvars*(idx_deb);
    n_samples = idx_fin - idx_deb + 1;
    fid.seek(skip_deb*4)  # *4 : conv offset int32 -> bytes
    if np.isinf(n_samples): n_samples=np.uint(1e6)

#    FenetreLecture_size = 10000 * Nvars;    
    FenetreLecture_size = n_samples * Nvars;    
    Trace=np.zeros(n_samples)
    
    n=0    
    while (1):
      Data0=scipy.fromfile(fid,'uint32', FenetreLecture_size)
      if len(Data0)==0: 
          n_samples=n 
          break
      Data0 = Data0[VarNr::Nvars]
      Trace[n:n+len(Data0)] = Data0
      n=n+len(Data0)
      if n >= n_samples:
        break
      
    Trace=Trace[0:n_samples-1];
    fid.close()
    
    Trace[Trace==UndefinedVal]=np.nan;
#If the parameter is set as signed         
    if Signe=='-': 
        Trace = Trace - 2**32*(Trace>=2**31)

# aplication of the gain        
    Trace = Trace * VarGain;
    
    return Trace

# -------------------------------------------------readbinary--------------------------------- 
# Input : DataFileName=String of full path of the binary file .bin
# Output : Variable = Array of array representing a matrix MxN where M:Number of parameters
#                                                                    N: Number of samples
#          Example: Data[i][j] calls the value representing the ith parameter for the jth sample
# Work : 1) The function open a file "Variable.txt" representing :
#               a. All the parameters' name : data[i][0]
#               b. Their corresponding number (i.e id) : data[i][1] (not used here)
#               c. If they are signed or unsigned data[i][2]
#        2) The function fills the array Variable with the function GetTraceFromFile 
#           that returns all the samples for a given parameter    
       
def readbinary(DataFileName,index_start, index_end, Nvars):
    
#    print("Start to read data from index " + str(index_start) + " to " + str(index_end) + "... ")
    FileNameIni = DataFileName[0:-4] + ".ini"
        
    fid=open(FileNameIni, 'r')
    FileIniNames=np.fromfile(fid, dtype=np.uint8)    
    fid.close()
    
#    Nvars = 235
#    Te   = 0.004
    
    with open('Variable.txt','r') as fd:
        data = np.loadtxt(fd, delimiter=' ', dtype={'names': ('col1', 'col2', 'col3'), 'formats': ('S30', 'f8', 'S1')})

    
    nbrRegimeVariable = np.uint(data[-1][1])+1 #total number of regime parameters
    nbrVariableRegime=np.where(data.astype(str)=='TkEd_Regime_ETC')[0][0] #index of variable representing the regime
    
#    print("Importing "+ str(len(data)) + " variables... ", end='')
    Variable = []
    for i in range (0,len(data)-nbrRegimeVariable): #Variable process != regime
        Variable.append(GetTraceFromFile(data[i][0].astype(str), FileIniNames, DataFileName, Nvars, index_start, index_end, data[i][2].astype(str)))
#        print(i)
#    print("Done!")
    
    # Handle the regime parameters #
        # np.uint(Variable[nbrVariableRegime][0]/(2**24)) : first regime parameters recorded at t=0
        # offset :  find the value representing the first regime in TkEd_Regime_ETC (i.e. Variable[offset] = Regime [0])
        # n : number of sample per variable
    offset = nbrRegimeVariable-np.uint(Variable[nbrVariableRegime][0]/(2**24)) 
    n=len(Variable[0]) 

    # init regime table    
    Regime=np.zeros((nbrRegimeVariable,n))+np.nan
    
    for i in range (offset,nbrRegimeVariable+offset):
    # We build one regime's signal by starting at one point, looping the on the
    # first 105 values, and looking for its value every 105 measurments.
        b=(np.uint64(Variable[nbrVariableRegime][(i%nbrRegimeVariable)::nbrRegimeVariable]) & 65535)
    # Because one value for the regime is correct for the next 105 measurments,
    # we scale to get the same number of samples as the other signals
        a= np.repeat(b,nbrRegimeVariable)
    # Here we create the shift in the storage 
    # i.e. the value for the first parameters might be unknown at the beginning so we will record Nan value 
#        start=i%nbrRegimeVariable
        start=0
        endmat=min(len(a)+start,n)
        Regime[i-offset][start:endmat]=a[0:n-start] # instantaneous values
#        Regime[i-offset]=a

        
    return Variable,Regime, data.astype(str)


