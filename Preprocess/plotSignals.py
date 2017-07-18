# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 17:34:30 2017

@author: i0A103166
"""
import pandas as pd
import numpy as np
from matplotlib import mlab
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import gridspec

#==============================================================================
# Functions
#==============================================================================
def plot_positions(Data): # POSITIONS MAP

    fig = plt.figure()
    fig.clear()
    
    XPos_name = 'X'
    YPos_name = 'Y'
    Pos_units = 'mm'
    
    ax0 = fig.add_subplot(1,1,1)
    ax0.grid(color='#DDDDDD')
    ax0.plot(Data['TkEd_pCM_Regle_X'], Data['TkEd_pCM_Regle_Y'], color='#000055')
    ax0.set_title('Axis Position')
    ax0.set_xlabel(XPos_name + ' [' + Pos_units + ']')
    ax0.set_ylabel(YPos_name + ' [' + Pos_units + ']')
    
    fig.subplots_adjust(left=0.15, bottom=0.1, top=0.90, right=0.98)
    
    plt.show()
    return fig

def plot_signals(Data,include,echantillon,operation,refAbsCurv):  
    if refAbsCurv == True: X= Data['MainGeom_AbsCurTot_mm']
    else: X = Data['Time']
    Data[include].plot(x=X,subplots=True,title='Echantillon: ' +str(echantillon)+ ' Operation: ' +str(operation)+ '')
    return plt.gcf()

def plot_statistics(Var,Data,DoPlotStatistics,DoPlotSpectrogram,echantillon,regime,AbscCurvRef): # STATISTICS CURVES
    fig = plt.figure()
    fig.clear()
    Raw = pd.DataFrame()    
    Raw['Time'] = Data['Time'].astype(np.float)
    Raw['AbsCurv'] = Data['MainGeom_AbsCurTot_mm'].astype(np.float)
    Raw['Values'] = Data[Var[0]].astype(np.float)
    Raw['XPos'] = Data['TkEd_pCM_Regle_X'].astype(np.float)
    Raw['YPos'] = Data['TkEd_pCM_Regle_Y'].astype(np.float)
    Raw['RelTime'] = Raw['Time'].sub(Raw['Time'][0])

    X = Data['TkEd_pCM_Regle_X']
    Y = Data['TkEd_pCM_Regle_Y']
    Var = Data[Var]
    
    # get text labels
    Var_name = Var.columns[0]
    Var_units = ''
    XPos_name = 'X'
    YPos_name = 'Y'
    Pos_units = 'mm'
    if AbscCurvRef == False:
        T=Raw['Time']
    else:
        T=Data['MainGeom_AbsCurTot_mm']
        
        
    fig.suptitle('Regime: ' + str(regime) + 'Echantillon: ' + str(echantillon), fontsize=20)
#    plt.title(filename,y=1.08)
    
    if DoPlotStatistics:
        
        # prepare grid space for subplots
        gs = gridspec.GridSpec(4, 2, width_ratios=[1.5, 1]) 
        
        # Plot 1 : direct signal
        axsig = fig.add_subplot(gs[0])
        axsig.grid(color='#DDDDDD')
        axsig.set_title('Statistics on \"' + Var_name + '\" variable')
        axsig.plot(T,Var[Var_name],'b', label=Var_name + ' [' + Var_units + ']')
        axsig.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL')
        
        # Plot 2 : Derivative signals
        ax2 = fig.add_subplot(gs[2], sharex=axsig)
        ax2.grid(color='#DDDDDD')
        ax2.plot(T,Var['dt_'+Var_name],color='#AA5500', label='1st Derivative [' + Var_units + '/s]')
        ax2.plot(T,Var['dt2_'+Var_name],color='#5500AA', label='2nd Derivative [' + Var_units + '/sÂ²]')
        ax2.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DERIVATIVES')
        
        # Plot 3 : Location signals
        ax3 = fig.add_subplot(gs[4], sharex=axsig)
        ax3.grid(color='#DDDDDD')
        ax3.plot(T,Var[Var_name],color='#0000FF', alpha=0.3, label=Var_name + ' [' + Var_units + ']')
        ax3.plot(T,Var['med_'+ Var_name],color='#0055AA', label='Median [' + Var_units + ']')
        ax3.plot(T,Var['min_'+ Var_name],color='#00AA00', label='Minimum [' + Var_units + ']')
        ax3.plot(T,Var['max_'+ Var_name],color='#AA0000', label='Maximum [' + Var_units + ']')
        ax3.legend(bbox_to_anchor=(1, 0.5), loc=6, title='TRACKING')
        
        # Plot 4 : Scattering signals
        ax4 = fig.add_subplot(gs[6], sharex=axsig)
        ax4.grid(color='#DDDDDD')
        ax4.plot(T,Var['var_'+ Var_name],color='#FF0000', label='Variance [(' + Var_units + ')Â²]')
        ax4.plot(T,Var['std_'+ Var_name],color='#CC00CC', label='Std Deviation [' + Var_units + ']')
        ax4.plot(T,Var['etp_'+ Var_name],color='#04B404', label='Shannons Entropy [(' + Var_units + ')Â²]')
        ax4.legend(bbox_to_anchor=(1, 0.5), loc=6, title='SCATTERING')
        
        plt.setp(axsig.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax3.get_xticklabels(), visible=False)
        ax4.set_xlabel('MainGeom_AbsCurTot_mm')
    
        HdlSel2, = ax2.plot([T[0],T[0]],
                            [ax2.get_ylim()[0],ax2.get_ylim()[1]],
                            color='#FF0000', alpha=0.7)
        HdlSel3, = ax3.plot([T[0],T[0]],
                            [ax3.get_ylim()[0],ax3.get_ylim()[1]],
                            color='#FF0000', alpha=0.7)
        HdlSel4, = ax4.plot([T[0],T[0]],
                            [ax4.get_ylim()[0],ax4.get_ylim()[1]],
                            color='#FF0000', alpha=0.7)    
        
        axeslist = [axsig,ax2,ax3,ax4]
        
    elif DoPlotSpectrogram:
        
        # prepare grid space for subplots
        gs = gridspec.GridSpec(2, 3, width_ratios=[1.3, 0.02, 1]) 
        
        # Plot 1 : direct signal
        axsig = fig.add_subplot(gs[0])
        axsig.grid(color='#DDDDDD')
        axsig.set_title('Spectrogram of \"' + Var_name + '\" variable')
        axsig.plot(T,Var[Var_name], color='#0000A0', label=Var_name + ' [' + Var_units + ']')
        axsig.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL')
        plt.setp([axsig.get_xticklabels() for a in fig.axes[:-1]], visible=False)
        
        # Plot 2 : Spectrogram
        Fs = 1/(4e-3)
        ax2 = fig.add_subplot(gs[3], sharex=axsig)
        spec_p, spec_frqs, spec_bins, spec_im = plt.specgram(Var[Var_name],
                                                     window=mlab.window_hanning,
                                                     NFFT=512,
                                                     Fs=Fs,
                                                     noverlap=64,
                                                     cmap='plasma') # cmap can be 'Greys' 'plasma' 'viridis'
        ax2.set_ylabel('Frequency [Hz]')
        plt.setp(axsig.get_xticklabels(), visible=False)
        ax2.set_xlabel('Time [sec]')

        # spectrum color bar
        ax3 = fig.add_subplot(gs[4])
        fig.colorbar(mappable=spec_im, cax=ax3)
        ax3.set_ylabel('Magnitude [dB]')
        
        HdlSel2, = ax2.plot([T[0],T[0]],
                            [ax2.get_ylim()[0],ax2.get_ylim()[1]],
                            color='#FFFFFF', alpha=0.5)
        
        axeslist = [axsig,ax2]
    else:
        gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1]) 
        
        # Plot 1 : direct signal
        axsig = fig.add_subplot(gs[0])
        axsig.grid(color='#DDDDDD')
#        ax1.set_title('Statistics on \"' + Var_name + '\" variable')
        axsig.plot(T,Var[Var_name],'b', label=Var_name + ' [' + Var_units + ']')
#        ax1.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL')
       
        axsig.set_ylabel(Var_name + ' [' + Var_units + ']')
        axsig.set_xlabel('Relative time [s]')
        
        
    axpos = fig.add_subplot(1,3,3)
    axpos.grid(color='#DDDDDD')
    axpos.plot(X, Y, color='#000055')
    axpos.set_title('Axis Position')
    axpos.set_xlabel(XPos_name + ' [' + Pos_units + ']')
    axpos.set_ylabel(YPos_name + ' [' + Pos_units + ']')
    
    head_width_set = (((max(X)-min(X))/20)\
                      +((max(Y)-min(Y))/20))/2
    head_length_set = head_width_set*1.5
    # trace begining arrow
    arr_dir_X = (X[10] - X[0])/10
    arr_dir_Y = (Y[10] - Y[0])/10
    axpos.arrow(X[0], Y[0], arr_dir_X, arr_dir_Y, 
              head_width=head_width_set, head_length=head_length_set, 
              color='#00DD00', alpha=0.3)
    # trace ending arrow
    arr_dir_X = (X.iloc[-1] - X.iloc[-11])/10
    arr_dir_Y = (Y.iloc[-1] - Y.iloc[-11])/10
    axpos.arrow(X.iloc[-1], Y.iloc[-1], arr_dir_X, arr_dir_Y, 
              head_width=head_width_set, head_length=head_length_set, 
              color='#DD0000', alpha=0.3)

    # Make subplots close to each other and hide x ticks for all but bottom plot
    fig.subplots_adjust(hspace=0.05)
    fig.subplots_adjust(left=0.05, bottom=0.05, top=0.92, right=0.99)    
    plt.show()
    # mouse click selection point/line
    HdlSelPos, = axpos.plot(Raw['XPos'][0], Raw['YPos'][0], marker="o", color='#FF0000', alpha=0.5)
    HdlSelSig, = axsig.plot([T[0],T[0]],
                            [axsig.get_ylim()[0],axsig.get_ylim()[1]],
                            color='#FF0000', alpha=0.5)    
    

    def onClick(event): # on mounse click on figure(1) actions
        m_x, m_y = event.x, event.y
        iNearest = -1
        if axpos == event.inaxes: # positions click finder
            x, y = axpos.transData.inverted().transform([m_x, m_y])
            print('Click on position : ')
            Point = pd.DataFrame()
            Point['X'] = [x]
            Point['Y'] = [y]
            Positions = Raw[['XPos','YPos']]
            iNearest = Positions.sub(np.full(Positions.shape,Point)).abs().sum(axis=1).argmin()
        elif event.inaxes in axeslist: # relative time click follower
            x,y = axsig.transData.inverted().transform([m_x, m_y])
            print('Click on signal : ')
            iNearest = T.sub(np.full(T.shape,x)).abs().argmin()
        
        if iNearest >= 0:
            nabs = Raw['AbsCurv'][iNearest]
            nx = Raw['XPos'][iNearest]
            ny = Raw['YPos'][iNearest]
            nval = Raw['Values'][iNearest]
            nt = Raw['RelTime'][iNearest]
            print('X=%.3f  ' % nx, end='')
            print('Y=%.3f  ' % ny, end='')
            print('Absissa=%.3f  ' % nabs, end='')
            print('Value=%.3f  ' % nval, end='')
            print('Time=%.3f' % nt)
            HdlSelPos.set_xdata(nx)
            HdlSelPos.set_ydata(ny)
            if AbscCurvRef == True : nt = nabs 
            HdlSelSig.set_xdata([nt, nt])
            HdlSelSig.set_ydata([axsig.get_ylim()[0],axsig.get_ylim()[1]])
            if DoPlotSpectrogram or DoPlotStatistics:
                HdlSel2.set_xdata([nt, nt])
                HdlSel2.set_ydata([ax2.get_ylim()[0],ax2.get_ylim()[1]])
            if DoPlotStatistics:
                HdlSel3.set_xdata([nt, nt])
                HdlSel3.set_ydata([ax3.get_ylim()[0],ax3.get_ylim()[1]])
                HdlSel4.set_xdata([nt, nt])
                HdlSel4.set_ydata([ax4.get_ylim()[0],ax4.get_ylim()[1]])
                
            fig.canvas.draw()
        
    fig.canvas.mpl_connect('button_press_event', onClick)
    
#    multi = MultiCursor(fig.canvas, axeslist, color='b', lw=1, horizOn=True, vertOn=True)
    fig.show()
    
    print('Done !')
    
    return fig



def plotStrat(regime,Data,fig_signal,axes,refAbsCurv):    
    # Plot the differentes strategies
    if refAbsCurv == True: X= Data['MainGeom_AbsCurTot_mm']
    else: X = Data['Time']    
    strat = Data['CurveType']
    
    strat_intern = strat[(strat).apply(np.fix)==7].index.values
    strat_extern = strat[(strat).apply(np.fix)==8].index.values
    strat_ebauche = strat[(strat).apply(np.fix)==5].index.values            
    strat_arret_axe = strat[(strat).apply(np.fix)==6].index.values    
                                          
    bound_intern=np.split(strat_intern, np.where(np.diff(strat_intern) != 1)[0]+1)
    bound_extern=np.split(strat_extern, np.where(np.diff(strat_extern) != 1)[0]+1)
    bound_ebauche=np.split(strat_ebauche, np.where(np.diff(strat_ebauche) != 1)[0]+1)
    bound_arret_axe=np.split(strat_arret_axe, np.where(np.diff(strat_arret_axe) != 1)[0]+1)        
    
    for i in range (0,len(axes)):  
        if len(bound_intern)>1 :
            for m in range (0,len(bound_intern)):
                axes[i].axvspan(X[min(bound_intern[m])],X[max(bound_intern[m])], alpha=0.5, color='red',clip_on=False,label='angle intern') 
        if len(bound_extern)>1 :        
            for n in range (0,len(bound_extern)):
                axes[i].axvspan(X[min(bound_extern[n])],X[max(bound_extern[n])], alpha=0.5, color='blue',clip_on=False)                 
        if len(bound_ebauche)>1 :
            for o in range (0,len(bound_ebauche)):
                axes[i].axvspan(X[min(bound_ebauche[o])],X[max(bound_ebauche[o])], alpha=0.5, color='green',clip_on=False)
        if len(bound_arret_axe)>1 :
            for p in range (0,len(bound_arret_axe)):
                axes[i].axvspan(X[min(bound_arret_axe[p])],X[max(bound_arret_axe[p])], alpha=0.5, color='cyan',clip_on=False)   
    
    #Legend
    red_patch = mpatches.Patch(color='red', label='intern')
    blue_patch = mpatches.Patch(color='blue', label='extern')
    green_patch = mpatches.Patch(color='green', label='ebauche')
    cyan_patch = mpatches.Patch(color='cyan', label='arret axe')
    fig_signal.legend(handles=[red_patch,blue_patch,green_patch,cyan_patch], labels=('intern','extern','ebauche','arret axe',))        
    
def plotAll(Data,VarPlot,VarStat,echantillon,regime,refAbsCurv):
     #==============================================================================
    # EXECUTION : Plot results
    #==============================================================================
        print('Plot results... ', end='')
        
        #Plot geometry of workpiece
        fig_geom=plot_positions(Data)
        
        #Plot signals in VarSelect except signals in VarExclude 
        fig_signal=plot_signals(Data,VarPlot,echantillon,regime,refAbsCurv)
        DoPlotStatistics=1
        DoPlotSpectrogram=0
        fig_stat=plot_statistics(VarStat,Data,DoPlotStatistics,DoPlotSpectrogram,echantillon,regime,refAbsCurv)
        
        #Plot strategies
        if {'CurveType'}.issubset(Data.columns):
            plotStrat(regime,Data,fig_signal,fig_signal.get_axes(),refAbsCurv)    
            plotStrat(regime,Data,fig_stat,fig_stat.get_axes()[0:-1],refAbsCurv)    