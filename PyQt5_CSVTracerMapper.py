

import sys
import glob, os
import pandas as pd
import numpy as np
import scipy.stats
import PyQt5.QtCore as Qtc
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as Qtg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
#from matplotlib import gridspec
import matplotlib.pyplot as plt
from matplotlib import mlab
import time
#import random 


class MainUI(Qtw.QDialog):
 
    def __init__(self, parent=None):
        # set form as parent entity, add Minimize, Maximize and Close buttons
        
        super().__init__(parent,
             flags=Qtc.Qt.WindowMaximizeButtonHint|Qtc.Qt.WindowMinimizeButtonHint|Qtc.Qt.WindowCloseButtonHint)
        self.title = 'CSV Tracer Mapper'
        self.left = 100
        self.top = 100
        self.width = 1680
        self.height = 900
        self.FilesList = []
        self.SignalsList = []
        self.Datadir = ''
        self.Filename = ''
        self.VarTime = 'Time'
        self.VarAbs = 'MainGeom_AbsCurTot_mm'
        self.Var1 = ''
        self.VarXPos = 'TkEd_pCM_Regle_X'
        self.VarYPos = 'TkEd_pCM_Regle_Y'
        self.MovingWindow = 125 # number of samples for moving calculations (! should be impair to avoid aliasing)
        self.LoadOnlyVar = 0
        self.loaded = False
        self.initWidgets()
 
    def initWidgets(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
       
        # create instance for plots
        self.canvas = PlotCanvas(self)
        self.canvas.setContentsMargins(0,0,0,0)
        
        # create instances for controls
        ctllayout = Qtw.QHBoxLayout()
        ctllayout.setContentsMargins(0,0,0,0)
        ctllayout.setSpacing(10)
        
        self.gbDataFile = Qtw.QGroupBox('Data file')
        self.gbDataFile.setContentsMargins(0,6,0,0)
#        self.gbDataFile.setAlignment(Qtc.Qt.AlignCenter|Qtc.Qt.AlignVCenter)
        dflayout = Qtw.QHBoxLayout()
        
        self.btDir = Qtw.QPushButton('...')
        self.btDir.setFont(Qtg.QFont('SansSerif', 10))
        self.btDir.clicked.connect(self.selectDir)
        self.btDir.setFixedWidth(30)
        dflayout.addWidget(self.btDir,1)
        
        self.cb1Label = Qtw.QLabel('Aquisition File :')
        self.cb1Label.setFont(Qtg.QFont('SansSerif', 10))
        self.cb1Label.setAlignment(Qtc.Qt.AlignRight|Qtc.Qt.AlignVCenter)
        dflayout.addWidget(self.cb1Label,1)
           
        self.cb1List = Qtw.QComboBox(self)
        self.cb1List.setFont(Qtg.QFont('SansSerif', 10))
        self.cb1List.activated[str].connect(self.onSelFile)
        dflayout.addWidget(self.cb1List,3)
        
        self.cb2Label = Qtw.QLabel('Signal 1:')
        self.cb2Label.setFont(Qtg.QFont('SansSerif', 10))
        self.cb2Label.setAlignment(Qtc.Qt.AlignRight|Qtc.Qt.AlignVCenter)
        dflayout.addWidget(self.cb2Label,1)
        
        self.cb2List = Qtw.QComboBox(self)
        self.cb2List.setFont(Qtg.QFont('SansSerif', 10))
        self.cb2List.activated[str].connect(self.onSelSignal)
        dflayout.addWidget(self.cb2List,3)
        
        self.cb3Label = Qtw.QLabel('Signal 2:')
        self.cb3Label.setFont(Qtg.QFont('SansSerif', 10))
        self.cb3Label.setAlignment(Qtc.Qt.AlignRight|Qtc.Qt.AlignVCenter)
        dflayout.addWidget(self.cb3Label,1)
        
        self.cb3List = Qtw.QComboBox(self)
        self.cb3List.setFont(Qtg.QFont('SansSerif', 10))
        self.cb3List.activated[str].connect(self.onSelSignal)
        dflayout.addWidget(self.cb3List,3)
        
#        self.ckAbsMode = Qtw.QCheckBox('Curve Abscissa Mode')
#        self.ckAbsMode.setFont(Qtg.QFont('SansSerif', 10))
#        self.ckAbsMode.toggled.connect(self.onAbsModeChange)
#        self.ckAbsMode.setChecked(False)
#        dflayout.addWidget(self.ckAbsMode,1)
        
        self.button1 = Qtw.QPushButton('Reload Data')
        self.button1.setFont(Qtg.QFont('SansSerif', 10, weight=Qtg.QFont.Bold))
        self.button1.setStyleSheet('background-color: #FF8800')
        self.button1.clicked.connect(self.onReloadData)
        self.button1.setHidden(True)
        dflayout.addWidget(self.button1,2)
        
        self.gbDataFile.setLayout(dflayout)
        ctllayout.addWidget(self.gbDataFile,10)
                       
        self.gbDispMode = Qtw.QGroupBox('Display mode')
        self.gbDispMode.setContentsMargins(0,6,0,0)
        self.gbDispMode.setAlignment(Qtc.Qt.AlignCenter|Qtc.Qt.AlignVCenter)
        dmlayout = Qtw.QHBoxLayout()
        
        self.rbDispMode = Qtw.QRadioButton('2 traces')
        self.rbDispMode.setFont(Qtg.QFont('SansSerif', 10))
        self.rbDispMode.Mode = 0
        self.rbDispMode.toggled.connect(self.onDispModeChange)
        self.rbDispMode.setChecked(True)
        dmlayout.addWidget(self.rbDispMode,1)
        
        self.rbDispMode = Qtw.QRadioButton('Statistics')
        self.rbDispMode.setFont(Qtg.QFont('SansSerif', 10))
        self.rbDispMode.Mode = 1
        self.rbDispMode.toggled.connect(self.onDispModeChange)
        dmlayout.addWidget(self.rbDispMode,1)
        
        self.rbDispMode = Qtw.QRadioButton('Spectrogram')
        self.rbDispMode.setFont(Qtg.QFont('SansSerif', 10))
        self.rbDispMode.Mode = 2
        self.rbDispMode.toggled.connect(self.onDispModeChange)
        dmlayout.addWidget(self.rbDispMode,1)
        self.gbDispMode.setLayout(dmlayout)
        ctllayout.addWidget(self.gbDispMode,3)
#        self.rbDispMode.setDisabled(True)
        
        self.gbNav = Qtw.QGroupBox('Plot control')
        self.gbNav.setContentsMargins(0,6,0,0)
        self.gbNav.setAlignment(Qtc.Qt.AlignCenter|Qtc.Qt.AlignVCenter)
        navlayout = Qtw.QHBoxLayout()

        # Plot vavigation buttons
        self.btNav1 = Qtw.QPushButton('Home')
        self.btNav1.setFont(Qtg.QFont('SansSerif', 10))
        self.btNav1.clicked.connect(self.navHome)
        navlayout.addWidget(self.btNav1,1)

        self.btNav2 = Qtw.QPushButton('Zoom')
        self.btNav2.setFont(Qtg.QFont('SansSerif', 10))
        self.btNav2.clicked.connect(self.navZoom)
        navlayout.addWidget(self.btNav2,1)
        
        self.btNav3 = Qtw.QPushButton('Pan')
        self.btNav3.setFont(Qtg.QFont('SansSerif', 10))
        self.btNav3.clicked.connect(self.navPan)
        navlayout.addWidget(self.btNav3,1)

        self.gbNav.setLayout(navlayout)
        ctllayout.addWidget(self.gbNav,3)
        
#        # create instance for status bar
#        self.status = Qtw.QStatusBar(self)
#        self.status.setFont(Qtg.QFont('SansSerif', 10))
#        self.status.setContentsMargins(0,0,0,0)
#        self.status.showMessage('Ready')

        # create instance for status bar
#        self.status = StatusMessage(self)

        # Set layout
        ctlwidget = Qtw.QWidget(self)
        ctlwidget.setLayout(ctllayout)
        
        layout = Qtw.QVBoxLayout()
        layout.setContentsMargins(2,2,2,0)
        layout.addWidget(ctlwidget,0)
        layout.addWidget(self.canvas,1)
#        layout.addWidget(self.status,0)
        
        self.setLayout(layout)
        self.show()
        
        self.selectDir()
        self.loadFilesList()
        
    def selectDir(self):
        self.Datadir = str(Qtw.QFileDialog.getExistingDirectory\
                           (self,
                            "Select Directory for CSV data files",
                            'D:/GFMS/Data/2017-06 - WEDM Process Analytics/1 - CSV conversion/')) + '/'
        
    def navHome(self):
        self.canvas.toolbar.home()
        self.btNav2.setFlat(False) # to release previous navigation
        self.btNav3.setFlat(False) # to release previous navigation
        
    def navZoom(self):
        self.canvas.toolbar.zoom()
        if self.btNav2.isFlat():
            self.btNav2.setFlat(False)
        else:
            self.btNav2.setFlat(True)
            self.btNav3.setFlat(False) # to release previous navigation
        
    def navPan(self):
        self.canvas.toolbar.pan()
        if self.btNav3.isFlat():
            self.btNav3.setFlat(False)
        else:
            self.btNav3.setFlat(True)
            self.btNav2.setFlat(False) # to release previous navigation    
        
    def onDispModeChange(self):
        self.rbDispMode = self.sender()
        if self.rbDispMode.isChecked():
            self.canvas.PlotMode = self.rbDispMode.Mode
            if self.loaded:
                if self.rbDispMode.Mode == 1 : 
                    self.CalculateStats() # Statistics mode selected : calculate data
                else:
                    self.canvas.redraw()
        
#    def onAbsModeChange(self):
#        self.canvas.AbsCurvMode = self.ckAbsMode.isChecked()

    def loadFilesList(self):
        os.chdir(self.Datadir)
        for file in glob.glob("*.csv"):
            self.FilesList += [file]
        self.cb1List.addItems(self.FilesList)
        
    def onSelFile(self, text):
        self.canvas.message = 'Please wait for preparation of the list of signals from \"' + text + '\"...'
        self.canvas.redraw()
        self.Filename = self.cb1List.currentText()
        self.loadSignalsList()
        if self.loaded and self.SignalsList != []:
            self.button1.setHidden(False)
        self.loaded = False
        self.LoadOnlyVar = 0

    def loadSignalsList(self):
        # Open CSV file of a real data set to import columns (header) names
        with open(self.Datadir + self.Filename, mode='r', encoding='utf-8') as csvfile:
            csvdata = pd.read_csv(csvfile, sep=';', dtype=str, nrows=1).columns
        if len(csvdata) > 1:
            self.SignalsList = csvdata.tolist()
            self.canvas.message = 'Please select signal form the list and click \"Reload Data\"...'
        else:
            self.SignalsList = []
            self.canvas.message = 'ERROR : this file does not have enougth data, please select another one.'
        self.canvas.redraw()
    
        self.cb2List.addItems(self.SignalsList)
        self.cb3List.addItems(['(no signal)'] + self.SignalsList)
        
    def onSelSignal(self, text):
        self.canvas.message = '\"' + text + '\" signal selected, please click \"Reload Data\" to update plots...'
        self.canvas.redraw()
        self.Var1 = self.cb2List.currentText()
        self.Var2 = self.cb3List.currentText()
        self.button1.setHidden(False)
        
    def onReloadData(self):
        self.button1.setHidden(True)
        self.loaded = False
        
        if self.LoadOnlyVar == 0: # change file / data set
            
            self.canvas.Raw = pd.DataFrame()
            self.canvas.Stats = pd.DataFrame()
            
            self.canvas.message = 'Please wait for data loading from file \"' + self.Filename + '\"...'
            self.canvas.redraw()

            self.repaint()
            
            ### Load data from CSV
            csvdata = pd.DataFrame()
            print('Loading full data from \"' + self.Filename + '\"... ', end='')
    
            # Prepare variables list
            VarList = [self.VarTime, self.VarAbs, self.Var1, self.VarXPos, self.VarYPos]
            if self.Var2 != '(no signal)':
                VarList += [self.Var2]

            # Open CSV file of a real data set
            with open(self.Datadir + self.Filename, mode='r', encoding='utf-8') as csvfile:
                csvdata = pd.read_csv(csvfile, sep=';', dtype=str, usecols=VarList)
            
            # convert values into floats
            self.canvas.Raw['Time'] = csvdata[self.VarTime].astype(np.float)
            self.canvas.Raw['AbsCurv'] = csvdata[self.VarAbs].astype(np.float)
            self.canvas.Raw['Values1'] = csvdata[self.Var1].astype(np.float)
            if self.Var2 != '(no signal)': self.canvas.Raw['Values2'] = csvdata[self.Var2].astype(np.float)
            self.canvas.Raw['XPos'] = csvdata[self.VarXPos].astype(np.float)
            self.canvas.Raw['YPos'] = csvdata[self.VarYPos].astype(np.float)
            
            # cacluate relative and delta times
            self.canvas.Raw['RelTime'] = self.canvas.Raw['Time'].sub(self.canvas.Raw['Time'][0])
            self.canvas.Raw['dTime'] = self.canvas.Raw['Time'].sub(self.canvas.Raw['Time'].shift(1)).fillna(0)
            print('Done !')
            
            # display information on data imported
            print('Trace is %d samples long ' % len(csvdata.values), end='')
            print('(%.3f ' % (self.canvas.Raw['RelTime'].values[-1] - self.canvas.Raw['RelTime'].values[0]), end = '')
            print(self.VarAbs + ')')
                 
        else:
            # load only variables form the same file
            self.canvas.message = 'Loading variable(s) from \"' + self.Filename + '\"... '
            self.canvas.redraw()

            self.repaint()
            
            csvdata = pd.DataFrame()
            
            # Prepare variables list
            VarList = [self.Var1]
            if self.Var2 != '(no signal)':
                VarList += [self.Var2]
                
            # Open CSV file of a real data set
            with open(self.Datadir + self.Filename, mode='r', encoding='utf-8') as csvfile:
                csvdata = pd.read_csv(csvfile, sep=';', dtype=str, usecols=VarList)
            
            # convert values into floats
            self.canvas.Raw['Values1'] = csvdata[self.Var1].astype(np.float)
            if self.Var2 != '(no signal)': self.canvas.Raw['Values2'] = csvdata[self.Var2].astype(np.float)
            
        # check moving window length
        if self.MovingWindow > (len(self.canvas.Raw['Values1'].values)):
            self.canvas.message = 'ERROR : MovingWindow value is bigger than data length'
            self.canvas.redraw()
        else:
            self.loaded = True # data are loaded
            self.canvas.filename = self.cb1List.currentText()
            
            # update plot labels
            self.canvas.Var1_name = self.Var1
            self.canvas.Var1_units = ''
            if self.Var2 != '(no signal)':
                self.canvas.Var2_name = self.Var2
                self.canvas.Var2_units = ''
            else:
                self.canvas.Var2_name = '' # no name will diseable signal
                self.canvas.Var2_units = ''
            if self.canvas.AbsCurvMode:
                self.canvas.Abs_name = self.VarAbs
                self.canvas.Abs_units = 'mm'
            else:
                self.canvas.Abs_name = self.VarTime
                self.canvas.Abs_units = 's'
            self.canvas.XPos_name = self.VarXPos
            self.canvas.YPos_name = self.VarYPos
            self.canvas.Pos_units = 'mm'
            
            if self.rbDispMode.Mode == 1: # Statistics display mode activated
                self.CalculateStats()
            else:
                self.LoadOnlyVar = 1
                self.canvas.message = 'Ready'
                self.canvas.redraw()
            
        self.rbDispMode.setDisabled(False)
        
        
    def CalculateStats(self):
        # CALUCULATE STATISTICS
        self.canvas.message = 'Process statistical signals... '
        self.canvas.redraw()
        self.repaint()
        
        # Calculate Velocity (1st derivative) as X' = [X(n)-X(n-1)]/dT
        self.canvas.Stats['Vel'] = self.canvas.Raw['Values1'].sub(self.canvas.Raw['Values1'].shift(1)).fillna(0).div(self.canvas.Raw['dTime']).fillna(0)
        
        # Calculate Acceleration (2nd derivative) as X" = [X'(n)-X'(n-1)]/dT
        self.canvas.Stats['Acc'] = self.canvas.Stats['Vel'].sub(self.canvas.Stats['Vel'].shift(1)).fillna(0).div(self.canvas.Raw['dTime']).fillna(0)
        
        # Calculate moving Median
        self.canvas.Stats['Med'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).median().to_frame()
        self.canvas.Stats['Med'][:(self.MovingWindow-1)] = self.canvas.Stats['Med'][(self.MovingWindow-1)]
        
#        # Calculate moving Standard deviation
#        self.canvas.Stats['Std'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).std().to_frame()
#        self.canvas.Stats['Std'][:(self.MovingWindow-1)] = self.canvas.Stats['Std'][(self.MovingWindow-1)]
        
        # Calculate moving Shannon's Entropy
        self.canvas.Stats['Etp'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).apply(scipy.stats.entropy).to_frame()
        self.canvas.Stats['Etp'][:(self.MovingWindow-1)] = self.canvas.Stats['Etp'][(self.MovingWindow-1)]
           
        # Calculate moving variance
        self.canvas.Stats['Var'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).var().to_frame()
        self.canvas.Stats['Var'][:(self.MovingWindow-1)] = self.canvas.Stats['Var'][(self.MovingWindow-1)]
        
        # Calculate moving minimum
        self.canvas.Stats['Min'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).min().to_frame()
        self.canvas.Stats['Min'][:(self.MovingWindow-1)] = self.canvas.Stats['Min'][(self.MovingWindow-1)]
           
        # Calculate moving maximum
        self.canvas.Stats['Max'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).max().to_frame()
        self.canvas.Stats['Max'][:(self.MovingWindow-1)] = self.canvas.Stats['Max'][(self.MovingWindow-1)]

        self.canvas.message = 'Ready'
        self.canvas.redraw()
        

class PlotCanvas(FigureCanvas):
#class PlotCanvas(Qtw.QWidget):
 
    def __init__(self, parent=None):
                
        self.fig = Figure()
        self.graph = FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        self.toolbar = NavigationToolbar(self, self.graph, self)
        self.toolbar.hide()
        
        self.Raw = pd.DataFrame()
        self.Stats = pd.DataFrame()
        self.Var1_name = ''
        self.Var2_name = ''
        self.Var1_units = ''
        self.Var2_units = ''
        self.Abs_name = ''
        self.Abs_units = ''
        self.XPos_name = ''
        self.YPos_name = ''
        self.Pos_units = ''
        self.AbsCurvMode = False
        self.PlotMode = 0
        self.message = ''
        self.filename = ''
 
    def redraw(self):
        
        self.fig.clf()
        
        if self.Raw.empty == False:
            
            self.fig.suptitle(self.filename, fontsize=20) 
        
            if self.AbsCurvMode:
                self.PlotsX = self.Raw['AbsCurv']
            else:
                self.PlotsX = self.Raw['RelTime']

            if self.PlotMode == 1 and self.Stats.empty == False : # STATISTICAL VIEW

                
                # Plot 1 : direct signal
                self.axsig = self.fig.add_axes([0.08, 0.70, 0.50, 0.20])
    #            axsig = self.fig.add_subplot(gs[0])
                self.axsig.clear()
                self.axsig.xaxis.grid(color='k', linestyle=':', linewidth=1, alpha=0.2)
                self.axsig.axhline(y=0, color='k', linestyle=':', linewidth=1).set_alpha(0.2)
                self.axsig.set_title('Statistics on \"' + self.Var1_name + '\" variable')
                self.axsig.plot(self.PlotsX, self.Raw['Values1'], color='#0000A0', label=self.Var1_name + ' [' + self.Var1_units + ']')
                self.axsig.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL', prop={'size':8})
                
                # Plot 2 : Tracking signals
                self.ax2 = self.fig.add_axes([0.08, 0.49, 0.50, 0.20], sharex=self.axsig)
    #            ax2 = self.fig.add_subplot(gs[2], sharex=axsig)
                self.ax2.clear()
                self.ax2.xaxis.grid(color='k', linestyle=':', linewidth=1, alpha=0.2)
                self.ax2.axhline(y=0, color='k', linestyle=':', linewidth=1).set_alpha(0.2)
                self.ax2.plot(self.PlotsX,self.Raw['Values1'],color='#0000FF', alpha=0.3, label=self.Var1_name + ' [' + self.Var1_units + ']')
                self.ax2.plot(self.PlotsX,self.Stats['Med'],color='#0055AA', label='Median [' + self.Var1_units + ']')
                self.ax2.plot(self.PlotsX,self.Stats['Min'],color='#00AA00', label='Minimum [' + self.Var1_units + ']')
                self.ax2.plot(self.PlotsX,self.Stats['Max'],color='#AA0000', label='Maximum [' + self.Var1_units + ']')
                self.ax2.legend(bbox_to_anchor=(1, 0.5), loc=6, title='TRACKING', prop={'size':8})
                
                # Plot 3 : Derivative signals
                self.ax3 = self.fig.add_axes([0.08, 0.28, 0.50, 0.20], sharex=self.axsig)
    #            ax3 = self.fig.add_subplot(gs[4], sharex=axsig)
                self.ax3.clear()
                
                lcolor = '#FF5500'
                llabel = 'Velocity [' + self.Var1_units + '/s]'
                self.ax3.xaxis.grid(color='k', linestyle=':', linewidth=1, alpha=0.2)
                self.ax3.axhline(y=0, color='k', linestyle=':', linewidth=1).set_alpha(0.2)
                lns1 = self.ax3.plot(self.PlotsX,self.Stats['Vel'],color=lcolor, label=llabel, alpha=0.7)
                self.ax3.tick_params('y', colors=lcolor, labelsize=8, direction='in')
                
                lcolor = '#5500FF'
                llabel = 'Acceleration [' + self.Var1_units + '/s²]'
                self.ax3b = self.ax3.twinx()
                self.ax3b.clear()
                lns2 = self.ax3b.plot(self.PlotsX,self.Stats['Acc'],color=lcolor, label=llabel, alpha=0.7)
                self.ax3b.tick_params('y', colors=lcolor, labelsize=8, direction='in')
                self.ax3b.yaxis.set_label_position('left')
                self.ax3b.yaxis.set_ticks_position('left')
                self.ax3b.spines['left'].set_position(('axes',-0.06))
                
                lns = lns1+lns2
                labs = [l.get_label() for l in lns]
                self.ax3b.legend(lns, labs, bbox_to_anchor=(1, 0.5), loc=6, title='DERIVATIVES', prop={'size':8})
                
                # Plot 4 : Scattering signals
                self.ax4 = self.fig.add_axes([0.08, 0.07, 0.50, 0.20], sharex=self.axsig)
    #            ax4 = self.fig.add_subplot(gs[6], sharex=axsig)
                self.ax4.clear()
                
                lcolor = '#C00060'
                llabel = 'Variance'
                self.ax4.xaxis.grid(color='k', linestyle=':', linewidth=1, alpha=0.2)
                self.ax4.axhline(y=0, color='k', linestyle=':', linewidth=1).set_alpha(0.2)
                lns1 = self.ax4.plot(self.PlotsX,self.Stats['Var'],color=lcolor, label=llabel, alpha=0.7)
                self.ax4.tick_params('y', colors=lcolor, labelsize=8, direction='in')       
        
                lcolor = '#00A0A0'
                llabel = 'Entropy'
                self.ax4b = self.ax4.twinx()
                self.ax4b.clear()
                lns2 = self.ax4b.plot(self.PlotsX,self.Stats['Etp'],color=lcolor, label=llabel, alpha=0.7)
                self.ax4b.tick_params('y', colors=lcolor, labelsize=8, direction='in')
                self.ax4b.yaxis.set_label_position('left')
                self.ax4b.yaxis.set_ticks_position('left')
                self.ax4b.spines['left'].set_position(('axes',-0.06))
                
                lns = lns1+lns2
                labs = [l.get_label() for l in lns]
                self.ax4b.legend(lns, labs, bbox_to_anchor=(1, 0.5), loc=6, title='SCATTERING', prop={'size':8})
                
    #            self.plt.setp(axsig.get_xticklabels(), visible=False)
    #            self.plt.setp(ax2.get_xticklabels(), visible=False)
    #            self.plt.setp(ax3.get_xticklabels(), visible=False)
                self.ax4.set_xlabel(self.Abs_name + ' [' + self.Abs_units + ']')
            
                self.HdlSel2, = self.ax2.plot([self.PlotsX[0],self.PlotsX[0]],
                                    [self.ax2.get_ylim()[0],self.ax2.get_ylim()[1]],
                                    color='#FF0000', alpha=0.5)
                self.HdlSel3, = self.ax3.plot([self.PlotsX[0],self.PlotsX[0]],
                                    [self.ax3.get_ylim()[0],self.ax3.get_ylim()[1]],
                                    color='#FF0000', alpha=0.5)
                self.HdlSel4, = self.ax4.plot([self.PlotsX[0],self.PlotsX[0]],
                                    [self.ax4.get_ylim()[0],self.ax4.get_ylim()[1]],
                                    color='#FF0000', alpha=0.5)    
                
                self.axeslist = [self.axsig,self.ax2,self.ax3b,self.ax4b]
                
            elif self.PlotMode == 2: # SPECTROGRAM (NOT WORKING FOR QT)
                
                # Plot 1 : direct signal
                self.axsig = self.fig.add_axes([0.1, 0.51, 0.50, 0.40])
                self.axsig.clear()
                self.axsig.grid(color='#DDDDDD')
                self.axsig.set_title('Spectrogram of \"' + self.Var1_name + '\" variable')
                self.axsig.plot(self.PlotsX, self.Raw['Values1'], color='#0000A0', label=self.Var1_name + ' [' + self.Var1_units + ']')
                self.axsig.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL', prop={'size':8})
    #            self.plt.setp([axsig.get_xticklabels() for a in self.fig.axes[:-1]], visible=False)
                
                # Plot 2 : Spectrogram
                self.ax2 = self.fig.add_axes([0.1, 0.1, 0.50, 0.40], sharex=self.axsig)
                self.ax2.clear()
                spec_p, spec_frqs, spec_bins, spec_im = plt.specgram(self.Raw['Values1'],
                                                             window=mlab.window_hanning,
                                                             NFFT=1024,
                                                             Fs=1/(4e-3),
                                                             noverlap=512,
                                                             mode='magnitude', 
                                                             scale='dB',
        #                                                     pad_to=4096,
                                                             cmap='gnuplot2') # cmap can be 'Greys' 'plasma' 'viridis'
                self.ax2.set_ylabel('Frequency [Hz]')
                self.ax2.set_xlabel('Time [sec]')
                
                self.HdlSel2, = self.ax2.plot([self.PlotsX[0],self.PlotsX[0]],
                                    [self.ax2.get_ylim()[0],self.ax2.get_ylim()[1]],
                                    color='#FFFFFF', alpha=0.5)
                
                self.axeslist = [self.axsig,self.ax2]
                
            else : # SINGLE / DUAL TRACES
                self.axsig = self.fig.add_axes([0.08, 0.51, 0.57, 0.40])
                self.axsig.clear()
                self.axsig.grid(color='#DDDDDD')
                self.axsig.plot(self.PlotsX, self.Raw['Values1'], color='#0000A0', label=self.Var1_name + ' [' + self.Var1_units + ']')
                self.axsig.set_ylabel(self.Var1_name + ' [' + self.Var1_units + ']')
                self.axsig.set_xlabel(self.Abs_name + ' [' + self.Abs_units + ']')
                
                self.ax2 = self.fig.add_axes([0.08, 0.1, 0.57, 0.40], sharex=self.axsig)
                self.ax2.clear()
                if self.Var2_name != '':
                    self.ax2.grid(color='#DDDDDD')
                    self.ax2.plot(self.PlotsX, self.Raw['Values2'], color='#00A000', label=self.Var2_name + ' [' + self.Var2_units + ']')
                    self.ax2.set_ylabel(self.Var2_name + ' [' + self.Var2_units + ']')
                    self.ax2.set_xlabel(self.Abs_name + ' [' + self.Abs_units + ']')
                
                self.HdlSel2, = self.ax2.plot([self.PlotsX[0],self.PlotsX[0]],
                                              [self.ax2.get_ylim()[0],self.ax2.get_ylim()[1]],
                                              color='#FF0000', alpha=0.5)
                
                self.axeslist = [self.axsig,self.ax2]
        
                
            # Positions map
            self.axpos = self.fig.add_axes([0.72, 0.1, 0.26, 0.80])
            self.axpos.clear()
            self.axpos.grid(color='#DDDDDD')
            self.axpos.plot(self.Raw['XPos'], self.Raw['YPos'], color='#0000A0')
            self.axpos.set_title('Axis Position')
            self.axpos.set_xlabel(self.XPos_name + ' [' + self.Pos_units + ']')
            self.axpos.set_ylabel(self.YPos_name + ' [' + self.Pos_units + ']')
            self.axpos.set_aspect('equal')
            
            # Start/End Arrows
            head_width_set = (((max(self.Raw['XPos'])-min(self.Raw['XPos']))/20)\
                              +((max(self.Raw['YPos'])-min(self.Raw['YPos']))/20))/2
            head_length_set = head_width_set*1.5
            # trace begining arrow
            arr_dir_X = (self.Raw['XPos'][100] - self.Raw['XPos'][0])/100
            arr_dir_Y = (self.Raw['YPos'][100] - self.Raw['YPos'][0])/100
            self.axpos.arrow(self.Raw['XPos'][0], self.Raw['YPos'][0], arr_dir_X, arr_dir_Y, 
                      head_width=head_width_set, head_length=head_length_set, 
                      color='#00DD00', alpha=0.3)
            # trace ending arrow
            arr_dir_X = (self.Raw['XPos'].values[-1] - self.Raw['XPos'].values[-101])/100
            arr_dir_Y = (self.Raw['YPos'].values[-1] - self.Raw['YPos'].values[-101])/100
            self.axpos.arrow(self.Raw['XPos'].values[-1], self.Raw['YPos'].values[-1], arr_dir_X, arr_dir_Y, 
                      head_width=head_width_set, head_length=head_length_set, 
                      color='#DD0000', alpha=0.3)
        
            # Make subplots close to each other and hide x ticks for all but bottom plot
            self.fig.subplots_adjust(hspace=0.05, wspace=0.05)
    #        self.fig.subplots_adjust(left=0.08, bottom=0.05, top=0.92, right=0.99)
            
            # mouse click selection point/line
            self.HdlSelPos, = self.axpos.plot(self.Raw['XPos'][0], self.Raw['YPos'][0], marker="o", color='#FF0000', alpha=0.5)
            self.HdlSelSig, = self.axsig.plot([self.PlotsX[0],self.PlotsX[0]],
                                    [self.axsig.get_ylim()[0],self.axsig.get_ylim()[1]],
                                    color='#FF0000', alpha=0.5)
            
            self.HdlMessage = self.fig.text(0.5, 0.005, self.message, {'weight': 'bold'}, horizontalalignment='center')
        else:
            self.fig.clear()
#            self.fig.patches.append(plt.Rectangle((0,0), self.get_width_height()[0], self.get_width_height()[1], color='#FFFFFF', alpha = 0.3))
            self.HdlMessage = self.fig.text(0.5, 0.5, self.message, {'weight': 'bold'}, horizontalalignment='center')

        self.draw()
        

    def mousePressEvent(self,event):
        super(PlotCanvas, self).mousePressEvent(event)
        
        if event.button() == Qtc.Qt.RightButton: # active on mouse right click only
            event.accept()
            m_x, m_y = event.x(), event.y()
            
            iNearest = -1
            nval2 = 0
            x, y = self.axsig.transData.inverted().transform([m_x, m_y])

            # chekc which plot was clicked on
            if x > self.axsig.get_xlim()[1]: # click on positions map
                x, y = self.axpos.transData.inverted().transform([m_x, (self.get_width_height()[1]-m_y)])
                Point = pd.DataFrame()
                Point['X'] = [x]
                Point['Y'] = [y]
                Positions = self.Raw[['XPos','YPos']]
                iNearest = Positions.sub(np.full(Positions.shape,Point)).abs().sum(axis=1).argmin()
            else: # click on signal traces
                iNearest = self.PlotsX.sub(np.full(self.PlotsX.shape,x)).abs().argmin()
            
            if iNearest >= 0:
                nabs = self.Raw['AbsCurv'][iNearest]
                nx = self.Raw['XPos'][iNearest]
                ny = self.Raw['YPos'][iNearest]
                nval1 = self.Raw['Values1'][iNearest]
                nt = self.Raw['RelTime'][iNearest]

                self.message = 'Clicked on Trace(s) : Time=%.3f    ' %nt
                self.message += self.Var1_name + '=%.3f    ' %nval1
                if self.Var2_name != '':
                    nval2 = self.Raw['Values2'][iNearest]
                    self.message += self.Var2_name + '=%.3f    ' %nval2
                self.message += '    Position : X=%.3f    ' %nx
                self.message += 'Y=%.3f    ' %ny
                self.message += 'Absissa=%.3f' %nabs
            
                self.HdlMessage.set_text(self.message)

                self.HdlSelPos.set_xdata(nx)
                self.HdlSelPos.set_ydata(ny)
                if self.AbsCurvMode:
                    nt = nabs
                self.HdlSelSig.set_xdata([nt, nt])
                self.HdlSelSig.set_ydata([self.axsig.get_ylim()[0],self.axsig.get_ylim()[1]])
                self.HdlSel2.set_xdata([nt, nt])
                self.HdlSel2.set_ydata([self.ax2.get_ylim()[0],self.ax2.get_ylim()[1]])
                if self.PlotMode == 1:
                    self.HdlSel3.set_xdata([nt, nt])
                    self.HdlSel3.set_ydata([self.ax3.get_ylim()[0],self.ax3.get_ylim()[1]])
                    self.HdlSel4.set_xdata([nt, nt])
                    self.HdlSel4.set_ydata([self.ax4.get_ylim()[0],self.ax4.get_ylim()[1]])
                self.draw()
        

if __name__ == '__main__':
    
    app = Qtc.QCoreApplication.instance()
    if app is None:
        app = Qtw.QApplication(sys.argv)
        
    ex = MainUI()
    exit
