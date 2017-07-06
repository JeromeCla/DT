#==============================================================================
# CURVE ABSCISSA TRANSFORM
#==============================================================================
#
# Description:
# Variables transformation from functions of time into funtion of curve 
# abcsissa
#
# Use the 2 main functions:
# CurvAbsTranform = Interpolate variable from time related into curve abscissa
# length related
# 
# CountRewindings = count the number of rewindings detected and return it in 
# the new linear abscissa system  
#
#==============================================================================
# Author : Bertrand Lavazais, Copyright +GF+ Machining Solutions 2017
#==============================================================================

import pandas as pd
import numpy as np
import math
import scipy.interpolate


def LinearAbsCurv(df_AbsCurv, str_NewName):
    
    # Convert values to float if required
    AbsCurv = df_AbsCurv.astype(np.float)
    
    # Generate linear space for new curve abscissa reference
    EndAbsCurv = math.ceil(max(AbsCurv.values)*10000)/10000 # 0.1um precision
    NbVal = math.ceil(max(AbsCurv.values)*10000) + 1 # number of indexes from given DeltaPos

    return pd.DataFrame(np.linspace(0, EndAbsCurv, NbVal), columns=[str_NewName])



def CurvAbsTranform(df_Variable, df_AbsCurv, str_NewName, str_RegressionKind):
    
    # Convert values to float if required
    AbsCurv = df_AbsCurv.astype(np.float)
    # Convert values to float if required
    Variable = df_Variable.astype(np.float)
    # interpolate values
    if str_RegressionKind == 'fast':  
        return pd.DataFrame(np.interp(LinearAbsCurv(df_AbsCurv, ''), AbsCurv, Variable), columns=[str_NewName])
    else:
        Interpolated = scipy.interpolate.interp1d(AbsCurv, Variable, kind=str_RegressionKind)
        return pd.DataFrame(Interpolated(LinearAbsCurv(df_AbsCurv,'')), columns=[str_NewName])
#    scipy.interpolate.interpn()

        


def CountRewindings(df_AbsCurv):
    
    # Convert values to float if required
    AbsCurv = df_AbsCurv.astype(np.float) - df_AbsCurv.astype(np.float).values[0]
    
    # Calculate delta length for each position
    DeltaAbsCurv = AbsCurv.values[1:]-AbsCurv.values[0:-1]
    DeltaAbsCurv = np.insert(DeltaAbsCurv, 0, 0) # (first is the reference = zero)
    
    # retain position of rewindings
    IterPos = np.round(np.sort(AbsCurv[np.where(DeltaAbsCurv<0)[0]])*10000)
    # mark rewindings iterations
    IterPos,IterNum = np.unique(IterPos.astype(np.int),return_counts=True)
    # Prepare new feature to link curve abscissa with iterations
    NbVal = math.ceil(max(AbsCurv.values)*10000) + 1 # calculate new linear abscissa positions
    Rewindings = np.zeros(NbVal)
    Rewindings[IterPos] = IterNum
    
    return pd.DataFrame(Rewindings,columns = ['Rewindings'])

def getDataAbsCurv(Data,str_RegressionKind):
    Data_new=pd.DataFrame()
    for k in range (0,len(Data.columns)):
       Data_new[Data.columns[k]]=CurvAbsTranform(Data[Data.columns[k]],Data['MainGeom_AbsCurTot_mm'],Data[Data.columns[k]].name,str_RegressionKind)
    Data_new['Rewindings'] = CountRewindings(Data['MainGeom_AbsCurTot_mm'])

    return Data_new
