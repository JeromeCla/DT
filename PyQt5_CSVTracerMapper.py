
import sys, glob, os, math
import pandas as pd
import numpy as np
import scipy.stats
import PyQt5.QtCore as Qtc
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as Qtg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib import mlab
import matplotlib.patches as mpatches
import sys
sys.path.insert(0, 'Preprocess')
import posttreatment as pt

class MainUI(Qtw.QDialog):
 
    def __init__(self, parent=None):
        
        # set form as parent entity, add Minimize, Maximize and Close buttons
        super().__init__(parent,
             flags=Qtc.Qt.WindowMaximizeButtonHint|Qtc.Qt.WindowMinimizeButtonHint|Qtc.Qt.WindowCloseButtonHint)
        
        self.title = 'CSV Tracer Mapper'
        self.version = 'v1.0'
        self.author = 'B.Lavazais & J.Clavel'
        self.copyright = 'Copyright +GF+ Machining Solutions 2017'
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
        self.synchroInterval = 500
        self.progressPieChars = ['\u25CB','\u25D4','\u25D1','\u25D5','\u25CF']
        
        self.popupInfo()
        
        self.initWidgets()
 
    def popupInfo(self):
        msg = Qtw.QMessageBox()
        msg.setIcon(Qtw.QMessageBox.Information)
        msg.setWindowTitle(self.title + ' ' + self.version)
        msg.setText('Trace and map positions of CSV files from EDM machines')
        msg.setInformativeText('Written by ' + self.author + '\n' +\
                               self.copyright)
#        msg.setDetailedText("The details are as follows...")
        msg.setStandardButtons(Qtw.QMessageBox.Ok)
        msg.exec_()
    
    def initWidgets(self):
        self.setWindowTitle(self.title + ' ' + self.version + '  -  ' + self.author + '  -  ' + self.copyright)
        self.setGeometry(self.left, self.top, self.width, self.height)
       
        # create instance for plots
        self.canvas = PlotCanvas(self)
        self.canvas.setContentsMargins(0,0,0,0)
        self.canvas.sig_DispSynchro[bool].connect(self.onDispSynchro)
        
        # create instances for controls
        ctllayout = Qtw.QHBoxLayout()
        ctllayout.setContentsMargins(0,0,0,0)
        ctllayout.setSpacing(10)
        
        self.gbDataFile = Qtw.QGroupBox('Data file')
        self.gbDataFile.setContentsMargins(0,6,0,0)
#        self.gbDataFile.setAlignment(Qtc.Qt.AlignCenter|Qtc.Qt.AlignVCenter)
        dflayout = Qtw.QHBoxLayout()
        
        self.btDir = Qtw.QPushButton('')
        self.btDir.setFont(Qtg.QFont('SansSerif', 10))
        self.btDir.clicked.connect(self.selectDir)
        self.btDir.setFixedWidth(30)
        self.btDir.setIcon(self.style().standardIcon(Qtw.QStyle.SP_DialogOpenButton))
#        self.btDir.setIcon(Qtw.QMessageBox.Information)
        self.btDir.setToolTip('Change files directory')
        dflayout.addWidget(self.btDir,0)
        
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
        self.cb2List.activated[str].connect(self.onSelSignal1)
        dflayout.addWidget(self.cb2List,3)
        
        self.cb3Label = Qtw.QLabel('Signal 2:')
        self.cb3Label.setFont(Qtg.QFont('SansSerif', 10))
        self.cb3Label.setAlignment(Qtc.Qt.AlignRight|Qtc.Qt.AlignVCenter)
        dflayout.addWidget(self.cb3Label,1)
        
        self.cb3List = Qtw.QComboBox(self)
        self.cb3List.setFont(Qtg.QFont('SansSerif', 10))
        self.cb3List.activated[str].connect(self.onSelSignal2)
        dflayout.addWidget(self.cb3List,3)
        
        self.cb4List = Qtw.QComboBox(self)
        self.cb4List.setFont(Qtg.QFont('SansSerif', 10))
        self.cb4List.activated[str].connect(self.onSelOperator)
        self.cb4List.addItems([' ', '+', '-', 'x', '/'])
        self.cb4List.setFixedWidth(32)
        self.cb4List.setDisabled(True)
        self.cb4List.setToolTip('Operator for Signal 2 :\n' + \
                                '(empty) independant signals\n' + \
                                '\"+\" add Signal 2 to Signal 1\n' + \
                                '\"-\" substract Signal 2 to Signal 1\n' + \
                                '\"x\" multiply Signal 2 to Signal 1\n' + \
                                '\"/\" divide Signal 2 to Signal 1')
        dflayout.addWidget(self.cb4List,0)
        
#        self.ckAbsMode = Qtw.QCheckBox('Curve Abscissa Mode')
#        self.ckAbsMode.setFont(Qtg.QFont('SansSerif', 10))
#        self.ckAbsMode.toggled.connect(self.onAbsModeChange)
#        self.ckAbsMode.setChecked(False)
#        dflayout.addWidget(self.ckAbsMode,1)
        
        self.btReload = Qtw.QPushButton('Reload Data')
        self.btReload.setFont(Qtg.QFont('SansSerif', 10, weight=Qtg.QFont.Bold))
        self.btReload.setIcon(self.style().standardIcon(Qtw.QStyle.SP_BrowserReload))
        self.btReload.setStyleSheet('background-color: #00FF88')
        self.btReload.clicked.connect(self.onReloadData)
        self.btReload.setHidden(True)
        
        self.btStrat = Qtw.QCheckBox('Show Strategies')
        self.btStrat.setFont(Qtg.QFont('SansSerif', 10, weight=Qtg.QFont.Bold))
        self.btStrat.toggled.connect(self.onShowStrat)
        dflayout.addWidget(self.btStrat,1)
        
        dflayout.addWidget(self.btReload,2)
        
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
        self.btNav1.setIcon(self.style().standardIcon(Qtw.QStyle.SP_DialogCancelButton))
        self.btNav1.clicked.connect(self.navHome)
        navlayout.addWidget(self.btNav1,1)

        self.btNav2 = Qtw.QPushButton('Zoom')
        self.btNav2.setFont(Qtg.QFont('SansSerif', 10))
        self.btNav2.setIcon(self.style().standardIcon(Qtw.QStyle.SP_FileDialogContentsView))
        self.btNav2.clicked.connect(self.navZoom)
        navlayout.addWidget(self.btNav2,1)
        
        self.btNav3 = Qtw.QPushButton('Pan')
        self.btNav3.setFont(Qtg.QFont('SansSerif', 10))
        self.btNav3.setIcon(self.style().standardIcon(Qtw.QStyle.SP_MediaSeekForward))
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
#        self.show()
        self.gbDispMode.setDisabled(True)
        self.gbNav.setDisabled(True)
        self.showMaximized()
        
        self.selectDir()
        
        
    def selectDir(self):
        self.Datadir = str(Qtw.QFileDialog.getExistingDirectory\
                           (self,
                            "Select Directory for CSV data files",
                            'D:/GFMS/Data/2017-06 - WEDM Process Analytics/1 - CSV conversion/')) + '/'
        self.loadFilesList()
        
    def disableControls(self):
        self.gbDataFile.setDisabled(True)
        self.gbDispMode.setDisabled(True)
        self.gbNav.setDisabled(True)
        
    def enableControls(self):
        self.gbDataFile.setEnabled(True)
        self.gbDispMode.setEnabled(True)
        self.gbNav.setEnabled(True)
        
    def navHome(self):
        # set home
        self.canvas.toolbar.home()
        # give back focus to plot
        self.canvas.setFocus()
        
    def navZoom(self):
        # toggle zoom
        self.canvas.toolbar.zoom()
        if self.btNav2.isFlat(): # zoom was active => desactivate it
            self.btNav2.setFlat(False)
        else: # zoom was not active => activate it
            self.btNav2.setFlat(True)    
            # release previous navigation action
            self.btNav3.setFlat(False)
        # give back focus to plot
        self.canvas.setFocus()
        
    def navPan(self):
        # toggle panning
        self.canvas.toolbar.pan()
        if self.btNav3.isFlat(): # pan was active => desactivate it
            self.btNav3.setFlat(False)
        else: # pan was not active => activate it
            self.btNav3.setFlat(True)
            # release previous navigation action
            self.btNav2.setFlat(False)
        # give back focus to plot
        self.canvas.setFocus()
        
    def onDispModeChange(self):
        self.rbDispMode = self.sender()
        if self.rbDispMode.isChecked():
            self.canvas.PlotMode = self.rbDispMode.Mode
            if self.canvas.dataLoaded:
                if self.rbDispMode.Mode == 1 : 
                    self.CalculateStats() # Statistics mode selected : calculate data
                elif self.rbDispMode.Mode == 3 :
                    self.loadBatches() # Load all batches of the same pass
                else: # direct signals mode
                    self.canvas.redraw()
                    self.canvas.setFocus()
    
    def onShowStrat(self):
        if self.btStrat.isChecked():
            self.canvas.PlotStrat = 1
            self.canvas.redraw()
        else: 
            self.canvas.PlotStrat = 0
            self.canvas.redraw()
        
#    def onAbsModeChange(self):
#        self.canvas.AbsCurvMode = self.ckAbsMode.isChecked()




    # DISP SYNCHRO
    
    def onDispSynchro(self):

        if self.canvas.SynchroMode == False:
            self.canvas.SynchroMode = True
            self.canvas.message = 'Please wait for data synchronization of all .csv files in directory...'
            self.disableControls()
            self.canvas.showDisable()
            self.repaint()
            
            # Load synchronized plots on the same position
            self.canvas.dataLoaded = False
            inc = 0
            for file in self.FilesList:
  
                self.canvas.message = 'Synchronizing data file %1d' %(inc+1) + \
                ' of ' + str(len(self.FilesList)) + ' : \"' + file + '\"... '               
                self.canvas.showMessage()
                self.repaint()
                
                # clear import frame
                csvdata = pd.DataFrame()
                # prepare list of variables
                VarList = [self.Var1, self.VarXPos, self.VarYPos]
                rowsSkipped = self.canvas.iNearest - self.synchroInterval
                rowsLoaded = 2*self.synchroInterval
                
                # Open CSV file of a real data set
                with open(self.Datadir + file, mode='r', encoding='utf-8') as csvfile:
                    csvdata = pd.read_csv(csvfile,
                                          sep=';',
                                          dtype=str,
                                          usecols=VarList,
                                          skiprows=rowsSkipped,
                                          nrows=rowsLoaded)

                self.canvas.Synch[inc] = csvdata[self.Var1].astype(np.float)
                
                inc += 1 
#                time.sleep(0.25)
            
            self.canvas.dataLoaded = True
            self.canvas.message = 'Double-click to go back to signal'
            self.canvas.redraw()
            
        else:
            self.canvas.SynchroMode = False
            self.enableControls()
            self.onReloadData()
            
        self.canvas.setFocus()



    def loadFilesList(self):
        self.cb1List.clear()
        self.FilesList.clear()
        os.chdir(self.Datadir)
        for file in glob.glob('*.csv'):
            self.FilesList += [file]
        self.cb1List.addItems(self.FilesList)
        if len(self.FilesList) > 0:
            self.canvas.message = 'Please select acquisition file from the list... '
            self.canvas.showDisable()
        else:
            self.canvas.message = 'ERROR : No CSV file vailable, please check directory... '
            self.canvas.showDisable()
        
        
    def onSelFile(self, text):
        self.canvas.message = 'Please wait for preparation of the list of signals from \"' + text + '\"...'
        self.canvas.showDisable()

        self.Filename = self.cb1List.currentText()
        self.loadSignalsList()
        if self.canvas.dataLoaded and self.SignalsList != []:
            self.btReload.setHidden(False)
        self.canvas.dataLoaded = False
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
            self.canvas.message = 'ERROR : Selected file does not have enougth data !'
        self.canvas.showMessage()
    
        self.cb2List.addItems(self.SignalsList)
        self.cb3List.addItems(['(no signal)'] + self.SignalsList)
        self.cb4List.setCurrentIndex(0)
        
    def onSelSignal1(self, text):
        self.canvas.message = '\"' + text + '\" signal selected, please click on \"Reload Data\" to refresh...'
        self.canvas.showDisable()
        self.Var1 = self.cb2List.currentText()
        self.Var2 = self.cb3List.currentText()
        self.btReload.setHidden(False)
            
    def onSelSignal2(self, text):
        if text == '(no signal)':
            self.cb4List.setCurrentIndex(0)
            self.cb4List.setDisabled(True)
        else:
            self.cb4List.setDisabled(False)
            self.canvas.message = '\"' + text + '\" signal selected, please click on \"Reload Data\" to refresh...'
            self.canvas.showDisable()
            self.btReload.setHidden(False)
        self.Var1 = self.cb2List.currentText()
        self.Var2 = self.cb3List.currentText()
  
    def onSelOperator(self, text):
        if self.canvas.dataLoaded:
            self.canvas.message = 'operator changed, please click on \"Reload Data\" to refresh...'
            self.canvas.showDisable()
            self.btReload.setHidden(False)
        
    def onReloadData(self):
        self.btReload.setHidden(True)
        self.canvas.dataLoaded = False
        
        self.canvas.showDisable()
        
        if self.LoadOnlyVar == 0: # change file / data set
            
            self.canvas.iNearest = 0 # to reset cursors
            self.canvas.Raw = pd.DataFrame()
            self.canvas.Stats = pd.DataFrame()
            
            msg = 'Please wait for full data loading from file \"' + self.Filename + '\"...'
            self.canvas.message = msg
            self.canvas.showMessage()
            self.repaint()
            
            # Prepare variables list
            if {self.VarTime}.issubset(self.SignalsList):
                VarList = [self.VarTime, self.Var1]
            else:
                self.canvas.message = 'ERROR : \"' + self.VarTime + '\" variable is missing'
                self.canvas.showMessage()
                return
                
            if {self.VarAbs}.issubset(self.SignalsList):
                VarList += [self.VarAbs]
                self.canvas.AbsAvailable = True
            else:
                self.canvas.AbsAvailable = False
                self.canvas.message = 'No curve abscissa variable available'
                self.canvas.showMessage()
                
            if {self.VarXPos,self.VarYPos}.issubset(self.SignalsList):
                VarList += [self.VarXPos, self.VarYPos]
                self.canvas.PosAvailable = True
            else:
                self.canvas.PosAvailable = False
                self.canvas.message = 'No position variable available'
                self.canvas.showMessage()

            if self.Var2 != '(no signal)':
                VarList += [self.Var2]
                
            VarList += ['Stra_Etat_TableActive','Stra_ModifCROV_Final','Operation']

            ### Load data from CSV
            filepath = self.Datadir + self.Filename
            csvreader = pd.read_csv(filepath,
                                    sep=';',
                                    dtype=str,
                                    usecols=VarList,
                                    chunksize=round(os.stat(filepath).st_size/8000))
            
            progress = 0
            csvdata = pd.DataFrame()
            for chunk in csvreader:
                self.canvas.message = msg + '\n' + self.progressPieChars[np.clip(progress,0,4)]
                self.canvas.showMessage()
                self.repaint()
                csvdata = pd.DataFrame.append(csvdata,chunk)
                progress +=1
                
                
            # convert values into floats
            self.canvas.Raw['Time'] = csvdata[self.VarTime].astype(np.float)
            
            if self.canvas.AbsAvailable: self.canvas.Raw['AbsCurv'] = csvdata[self.VarAbs].astype(np.float)
            
            self.canvas.Raw['Values1'] = csvdata[self.Var1].astype(np.float)
            data = pd.DataFrame()
            data['Stra_Etat_TableActive']=csvdata['Stra_Etat_TableActive'].astype(np.float)
            data['Stra_ModifCROV_Final']=csvdata['Stra_ModifCROV_Final'].astype(np.float)
            
            self.canvas.Raw['Strat'] = pt.Generate_CurveType(csvdata.iloc[-1]['Operation'],data) 
            # Plot the differentes strategies
            strat = self.canvas.Raw['Strat']    
            strat_intern = strat[(strat).apply(np.fix)==7].index.values
            strat_extern = strat[(strat).apply(np.fix)==8].index.values
            strat_ebauche = strat[(strat).apply(np.fix)==5].index.values            
            strat_arret_axe = strat[(strat).apply(np.fix)==6].index.values    
            
                                      
            bound_intern=np.split(strat_intern, np.where(np.diff(strat_intern) != 1)[0]+1)
            self.canvas.intern=bound_intern
            bound_extern=np.split(strat_extern, np.where(np.diff(strat_extern) != 1)[0]+1)
            self.canvas.extern=bound_extern
            bound_ebauche=np.split(strat_ebauche, np.where(np.diff(strat_ebauche) != 1)[0]+1)
            self.canvas.ebauche=bound_ebauche
            bound_arret_axe=np.split(strat_arret_axe, np.where(np.diff(strat_arret_axe) != 1)[0]+1)  
            self.canvas.arret_axe=bound_arret_axe

                
            
            if self.Var2 != '(no signal)':
                self.canvas.Raw['Values2'] = csvdata[self.Var2].astype(np.float)
                self.canvas.Var2_name = self.Var2
                if self.cb4List.currentText() == '+': 
                    self.canvas.Raw['Values2'] = self.canvas.Raw['Values1'].add(self.canvas.Raw['Values2'])
                    self.canvas.Var2_name = self.Var1 + ' + ' + self.Var2
                elif self.cb4List.currentText() == '-':
                    self.canvas.Raw['Values2'] = self.canvas.Raw['Values1'].sub(self.canvas.Raw['Values2'])
                    self.canvas.Var2_name = self.Var1 + ' - ' + self.Var2
                elif self.cb4List.currentText() == 'x':
                    self.canvas.Raw['Values2'] = self.canvas.Raw['Values1'].mul(self.canvas.Raw['Values2'])
                    self.canvas.Var2_name = self.Var1 + ' x ' + self.Var2
                elif self.cb4List.currentText() == '/':
                    self.canvas.Raw['Values2'] = self.canvas.Raw['Values1'].div(self.canvas.Raw['Values2'])
                    self.canvas.Var2_name = self.Var1 + ' / ' + self.Var2
            else:
                self.canvas.Var2_name = '' # no name will diseable signal
                    
            if self.canvas.PosAvailable:
                self.canvas.Raw['XPos'] = csvdata[self.VarXPos].astype(np.float)
                self.canvas.Raw['YPos'] = csvdata[self.VarYPos].astype(np.float)
            
            # cacluate relative and delta times
            self.canvas.Raw['RelTime'] = self.canvas.Raw['Time'].sub(self.canvas.Raw['Time'][0])
            self.canvas.Raw['dTime'] = self.canvas.Raw['Time'].sub(self.canvas.Raw['Time'].shift(1)).fillna(0)
#            print('Done !')
            
            # display information on data imported
            print('Trace is %d samples long ' % len(csvdata.values), end='')
            print('(%.3f ' % (self.canvas.Raw['RelTime'].values[-1] - self.canvas.Raw['RelTime'].values[0]), end = '')
            print(self.VarAbs + ')')
                 
        else:
            # load only variables form the same file
            msg = 'Please wait for loading variable(s) from file \"' + self.Filename + '\"...'
            self.canvas.message = msg
            self.canvas.showMessage()
            self.repaint()
            
            # Prepare variables list
            VarList = [self.Var1]
            if self.Var2 != '(no signal)':
                VarList += [self.Var2]
                
            ### Load data from CSV
            filepath = self.Datadir + self.Filename
            csvreader = pd.read_csv(filepath,
                                    sep=';',
                                    dtype=str,
                                    usecols=VarList,
                                    chunksize=round(os.stat(filepath).st_size/8000))
            
            progress = 0
            csvdata = pd.DataFrame()
            for chunk in csvreader:
#                print('\u2588',end='')
                self.canvas.message = msg + '\n' + self.progressPieChars[np.clip(progress,0,4)]
                self.canvas.showMessage()
                self.repaint()
                csvdata = pd.DataFrame.append(csvdata,chunk)
                progress +=1
            
            # convert values into floats
            self.canvas.Raw['Values1'] = csvdata[self.Var1].astype(np.float)
            if self.Var2 != '(no signal)':
                self.canvas.Raw['Values2'] = csvdata[self.Var2].astype(np.float)
                self.canvas.Var2_name = self.Var2
                if self.cb4List.currentText() == '+': 
                    self.canvas.Raw['Values2'] = self.canvas.Raw['Values1'].add(self.canvas.Raw['Values2'])
                    self.canvas.Var2_name = self.Var1 + ' + ' + self.Var2
                elif self.cb4List.currentText() == '-':
                    self.canvas.Raw['Values2'] = self.canvas.Raw['Values1'].sub(self.canvas.Raw['Values2'])
                    self.canvas.Var2_name = self.Var1 + ' - ' + self.Var2
                elif self.cb4List.currentText() == 'x':
                    self.canvas.Raw['Values2'] = self.canvas.Raw['Values1'].mul(self.canvas.Raw['Values2'])
                    self.canvas.Var2_name = self.Var1 + ' x ' + self.Var2
                elif self.cb4List.currentText() == '/':
                    self.canvas.Raw['Values2'] = self.canvas.Raw['Values1'].div(self.canvas.Raw['Values2'])
                    self.canvas.Var2_name = self.Var1 + ' / ' + self.Var2
            else:
                self.canvas.Var2_name = '' # no name will diseable signal
            
        # check moving window length
        if self.MovingWindow > (len(self.canvas.Raw['Values1'].values)):
            self.canvas.message = 'ERROR : MovingWindow value is bigger than data length'
            self.canvas.showMessage()
            return
        else:
            self.canvas.dataLoaded = True # data are loaded
            self.canvas.filename = self.cb1List.currentText()
            
            # update plot labels
            self.canvas.Var1_name = self.Var1
            self.canvas.Var1_units = ''
            
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
                self.canvas.showMessage()
        
        # sucess : refresh and enable displays
        self.enableControls()
        self.rbDispMode.setDisabled(False)
        self.canvas.redraw()
        self.canvas.setFocus()
        
        
    def CalculateStats(self):
        # CALUCULATE STATISTICS
        msg = 'Please wait for processing of statistical signals... '
        
        self.canvas.message = msg + '\n' + self.progressPieChars[1]
        self.canvas.showDisable()
        self.repaint()
        
        # Calculate Velocity (1st derivative) as X' = [X(n)-X(n-1)]/dT
        self.canvas.Stats['Vel'] = self.canvas.Raw['Values1'].sub(self.canvas.Raw['Values1'].shift(1)).fillna(0).div(self.canvas.Raw['dTime']).fillna(0)
        
        # Calculate Acceleration (2nd derivative) as X" = [X'(n)-X'(n-1)]/dT
        self.canvas.Stats['Acc'] = self.canvas.Stats['Vel'].sub(self.canvas.Stats['Vel'].shift(1)).fillna(0).div(self.canvas.Raw['dTime']).fillna(0)
        
        self.canvas.message = msg + '\n' + self.progressPieChars[2]
        self.canvas.showMessage()        
        self.repaint()
        
        # Calculate moving Median
        self.canvas.Stats['Med'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).median().to_frame()
        self.canvas.Stats['Med'][:(self.MovingWindow-1)] = self.canvas.Stats['Med'][(self.MovingWindow-1)]

        # Calculate moving minimum
        self.canvas.Stats['Min'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).min().to_frame()
        self.canvas.Stats['Min'][:(self.MovingWindow-1)] = self.canvas.Stats['Min'][(self.MovingWindow-1)]
           
        # Calculate moving maximum
        self.canvas.Stats['Max'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).max().to_frame()
        self.canvas.Stats['Max'][:(self.MovingWindow-1)] = self.canvas.Stats['Max'][(self.MovingWindow-1)]

        self.canvas.message = msg + '\n' + self.progressPieChars[3]
        self.canvas.showMessage()       
        self.repaint()
        
#        # Calculate moving Standard deviation
#        self.canvas.Stats['Std'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).std().to_frame()
#        self.canvas.Stats['Std'][:(self.MovingWindow-1)] = self.canvas.Stats['Std'][(self.MovingWindow-1)]
        
        # Calculate moving Shannon's Entropy
        self.canvas.Stats['Etp'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).apply(scipy.stats.entropy).to_frame()
        self.canvas.Stats['Etp'][:(self.MovingWindow-1)] = self.canvas.Stats['Etp'][(self.MovingWindow-1)]
           
        # Calculate moving variance
        self.canvas.Stats['Var'] = pd.Series.rolling(self.canvas.Raw['Values1'], window=self.MovingWindow, center=False).var().to_frame()
        self.canvas.Stats['Var'][:(self.MovingWindow-1)] = self.canvas.Stats['Var'][(self.MovingWindow-1)]
        
        self.canvas.message = 'Ready'
        self.canvas.redraw()



class PlotCanvas(FigureCanvas):
#class PlotCanvas(Qtw.QWidget):
 
    sig_DispSynchro = Qtc.pyqtSignal(bool)
    
    def __init__(self, parent=None):
                
        self.fig = Figure()
        self.graph = FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        self.toolbar = NavigationToolbar(self, self.graph, self)
        self.toolbar.hide()
        
        self.Raw = pd.DataFrame()
        self.Stats = pd.DataFrame()
        self.Synch = pd.DataFrame()
        self.intern = []
        self.extern = []
        self.arret_axe = []
        self.ebauche = []
        
        self.Var1_name = ''
        self.Var2_name = ''
        self.Var1_units = ''
        self.Var2_units = ''
        self.Abs_name = ''
        self.Abs_units = ''
        self.XPos_name = ''
        self.YPos_name = ''
        self.Pos_units = ''
        
        self.message = ''
        self.HdlMessage = None
        self.filename = ''
        self.PlotMode = 0
        self.PlotStrat = 0
        self.AbsCurvMode = False
        self.dataLoaded = False
        self.iNearest = 0
        self.SynchroMode = False
        self.AbsAvailable = False
        self.PosAvailable = False
        self.disabled = False
        
    def showDisable(self):
        if self.disabled:
            self.showMessage()
        else:
            self.disabled = True
            self.fig.suptitle('')
            if self.HdlMessage != None : self.HdlMessage.set_text('')
            self.draw()
            self.fig.patches.append(plt.Rectangle((0,0), self.get_width_height()[0], self.get_width_height()[1], color='#E0E0E0', alpha = 0.8))
            self.HdlMessage = self.fig.text(0.5, 0.5, self.message, {'weight': 'bold','fontsize': '18'}, horizontalalignment='center')
            self.draw()
        
    def showMessage(self):
        self.HdlMessage.set_text(self.message)
        self.draw()

    def redraw(self):
                
        if self.Raw.empty or self.dataLoaded == False:
            self.showDisable()
            return

        self.disabled = False
        self.fig.clf()        
        self.fig.suptitle(self.filename, fontsize=18, weight='bold') 
    
        if self.AbsCurvMode and self.AbsAvailable:
            self.PlotsX = self.Raw['AbsCurv']
        else:
            self.PlotsX = self.Raw['RelTime']       
        
        if self.PlotMode == 1 and self.Stats.empty == False : # STATISTICAL VIEW

            #Check if position have to be plotted
            if self.PosAvailable: 
                tracesWidth = 0.50
            else:
                tracesWidth = 0.80
                
            # Plot 1 : direct signal
            self.axsig = self.fig.add_axes([0.08, 0.70, tracesWidth, 0.20])
            self.axsig.clear()
            self.axsig.xaxis.grid(color='k', linestyle=':', linewidth=1, alpha=0.2)
            self.axsig.axhline(y=0, color='k', linestyle=':', linewidth=1).set_alpha(0.2)
            self.axsig.set_title('Statistics on \"' + self.Var1_name + '\" variable')
            self.axsig.plot(self.PlotsX, self.Raw['Values1'], color='#0000A0', label=self.Var1_name + ' [' + self.Var1_units + ']')
            self.axsig.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL', prop={'size':8})
            
            # Plot 2 : Tracking signals
            self.ax2 = self.fig.add_axes([0.08, 0.49, tracesWidth, 0.20], sharex=self.axsig)
            self.ax2.clear()
            self.ax2.xaxis.grid(color='k', linestyle=':', linewidth=1, alpha=0.2)
            self.ax2.axhline(y=0, color='k', linestyle=':', linewidth=1).set_alpha(0.2)
            self.ax2.plot(self.PlotsX,self.Raw['Values1'],color='#0000FF', alpha=0.3, label=self.Var1_name + ' [' + self.Var1_units + ']')
            self.ax2.plot(self.PlotsX,self.Stats['Med'],color='#0055AA', label='Median [' + self.Var1_units + ']')
            self.ax2.plot(self.PlotsX,self.Stats['Min'],color='#00AA00', label='Minimum [' + self.Var1_units + ']')
            self.ax2.plot(self.PlotsX,self.Stats['Max'],color='#AA0000', label='Maximum [' + self.Var1_units + ']')
            self.ax2.legend(bbox_to_anchor=(1, 0.5), loc=6, title='TRACKING', prop={'size':8})
            
            # Plot 3 : Derivative signals
            self.ax3 = self.fig.add_axes([0.08, 0.28, tracesWidth, 0.20], sharex=self.axsig)
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
            self.ax4 = self.fig.add_axes([0.08, 0.07, tracesWidth, 0.20], sharex=self.axsig)
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
        
            # cursor line on signals traces
            self.HdlSel2, = self.ax2.plot([self.PlotsX[self.iNearest],
                                           self.PlotsX[self.iNearest]],
                                          [self.ax2.get_ylim()[0],
                                           self.ax2.get_ylim()[1]],
                                           color='#FF0000', alpha=0.5)
            self.HdlSel3, = self.ax3.plot([self.PlotsX[self.iNearest],
                                           self.PlotsX[self.iNearest]],
                                          [self.ax3.get_ylim()[0],
                                           self.ax3.get_ylim()[1]],
                                           color='#FF0000', alpha=0.5)
            self.HdlSel4, = self.ax4.plot([self.PlotsX[self.iNearest],
                                           self.PlotsX[self.iNearest]],
                                          [self.ax4.get_ylim()[0],
                                           self.ax4.get_ylim()[1]],
                                           color='#FF0000', alpha=0.5)    
            
        elif self.PlotMode == 2: # SPECTROGRAM (NOT WORKING FOR QT)
            
            #Check if position have to be plotted
            if self.PosAvailable: 
                tracesWidth = 0.50
            else:
                tracesWidth = 0.80    
        
            # Plot 1 : direct signal
            self.axsig = self.fig.add_axes([0.1, 0.51, tracesWidth, 0.40])
            self.axsig.clear()
            self.axsig.grid(color='#DDDDDD')
            self.axsig.set_title('Spectrogram of \"' + self.Var1_name + '\" variable')
            self.axsig.plot(self.PlotsX, self.Raw['Values1'], color='#0000A0', label=self.Var1_name + ' [' + self.Var1_units + ']')
            self.axsig.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL', prop={'size':8})
 
#                self.plt.setp([axsig.get_xticklabels() for a in self.fig.axes[:-1]], visible=False)
            
            # Plot 2 : Spectrogram
            self.ax2 = self.fig.add_axes([0.1, 0.1, tracesWidth, 0.40], sharex=self.axsig)
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
            self.ax2.set_xlabel(self.Abs_name + ' [' + self.Abs_units + ']')
            
            # spectrum color bar
            self.ax3 = self.fig.add_axes([tracesWidth+0.11, 0.1, 0.01, 0.40], sharex=self.axsig)
            self.fig.colorbar(mappable=spec_im, cax=self.ax3)
            
            # cursor line on signal trace
            self.HdlSel2, = self.ax2.plot([self.PlotsX[self.iNearest],
                                           self.PlotsX[self.iNearest]],
                                          [self.ax2.get_ylim()[0],
                                           self.ax2.get_ylim()[1]],
                                           color='#FFFFFF', alpha=0.5)
            
        else : # SINGLE / DUAL TRACES
        
            #Check if position have to be plotted
            if self.PosAvailable: 
                tracesWidth = 0.57
            else:
                tracesWidth = 0.90   
        
            # Plot 1 : direct signal 1
            self.axsig = self.fig.add_axes([0.08, 0.51, tracesWidth, 0.40])
            self.axsig.clear()
            self.axsig.grid(color='#DDDDDD')
            self.axsig.plot(self.PlotsX, self.Raw['Values1'], color='#0000A0', label=self.Var1_name + ' [' + self.Var1_units + ']')
            self.axsig.set_ylabel(self.Var1_name + ' [' + self.Var1_units + ']')
            
            # Plot 2 : direct signal 2 (if any)
            self.ax2 = self.fig.add_axes([0.08, 0.1, tracesWidth, 0.40], sharex=self.axsig)
            self.ax2.clear()
            if self.Var2_name != '':
                self.ax2.grid(color='#DDDDDD')
                self.ax2.plot(self.PlotsX, self.Raw['Values2'], color='#00A000', label=self.Var2_name + ' [' + self.Var2_units + ']')
                self.ax2.set_ylabel(self.Var2_name + ' [' + self.Var2_units + ']')
                
            self.ax2.set_xlabel(self.Abs_name + ' [' + self.Abs_units + ']')
            
            # cursor line on signal trace
            self.HdlSel2, = self.ax2.plot([self.PlotsX[self.iNearest],
                                           self.PlotsX[self.iNearest]],
                                          [self.ax2.get_ylim()[0],
                                           self.ax2.get_ylim()[1]],
                                           color='#FF0000', alpha=0.5)
    
    
        # cursor line on signal trace (common to all display modes)
        self.HdlSelSig, = self.axsig.plot([self.PlotsX[self.iNearest],
                                           self.PlotsX[self.iNearest]],
                                          [self.axsig.get_ylim()[0],
                                           self.axsig.get_ylim()[1]],
                                           color='#FF0000', alpha=0.5)
    
        # messages/status bar
        self.HdlMessage = self.fig.text(0.5, 0.005, self.message, {'weight': 'bold'}, horizontalalignment='center')
    
        if self.PosAvailable:  
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
            head_width_set = (((max(self.Raw['XPos'])-min(self.Raw['XPos']))/30)\
                              +((max(self.Raw['YPos'])-min(self.Raw['YPos']))/30))/2
            head_length_set = head_width_set*1.5
            dir_len =  math.ceil(len(self.Raw.values)/500)
            # trace begining arrow
            arr_dir_X = (self.Raw['XPos'][dir_len] - self.Raw['XPos'][0])/dir_len
            arr_dir_Y = (self.Raw['YPos'][dir_len] - self.Raw['YPos'][0])/dir_len
            self.axpos.arrow(self.Raw['XPos'][0], self.Raw['YPos'][0], arr_dir_X, arr_dir_Y, 
                      head_width=head_width_set, head_length=head_length_set, 
                      color='#00FF60', alpha=0.3)
            # trace ending arrow
            arr_dir_X = (self.Raw['XPos'].values[-1] - self.Raw['XPos'].values[-(dir_len+1)])/dir_len
            arr_dir_Y = (self.Raw['YPos'].values[-1] - self.Raw['YPos'].values[-(dir_len+1)])/dir_len
            self.axpos.arrow(self.Raw['XPos'].values[-1], self.Raw['YPos'].values[-1], arr_dir_X, arr_dir_Y, 
                      head_width=head_width_set, head_length=head_length_set, 
                      color='#FF6000', alpha=0.3)
        
            # Make subplots close to each other and hide x ticks for all but bottom plot
            self.fig.subplots_adjust(hspace=0.05, wspace=0.05)
            
            # cursor dot on positions map
            self.HdlSelPos, = self.axpos.plot(self.Raw['XPos'][self.iNearest],
                                              self.Raw['YPos'][self.iNearest],
                                              marker="o", color='#FF0000', alpha=0.5)
            
        if self.PlotStrat == 1:  
            self.onStrat()        
            
        self.draw()
        
    def onStrat(self):
        
        bound_intern=self.intern
        bound_extern=self.extern
        bound_ebauche=self.ebauche
        bound_arret_axe=self.arret_axe
        axes = self.fig.get_axes()[0:-1]
        
        for i in range (0,len(axes)):
            if len(bound_intern)>1 :
                for m in range (0,len(bound_intern)):
                    axes[i].axvspan(self.PlotsX[min(bound_intern[m])],self.PlotsX[max(bound_intern[m])], alpha=0.5, color='yellow',clip_on=True)
            if len(bound_extern)>1 :        
                for n in range (0,len(bound_extern)):
                    axes[i].axvspan(self.PlotsX[min(bound_extern[n])],self.PlotsX[max(bound_extern[n])], alpha=0.5, color='blue',clip_on=True)                 
            if len(bound_ebauche)>1 :
                for o in range (0,len(bound_ebauche)):
                    axes[i].axvspan(self.PlotsX[min(bound_ebauche[o])],self.PlotsX[max(bound_ebauche[o])], alpha=0.5, color='green',clip_on=True)
            if len(bound_arret_axe)>1 :
                for p in range (0,len(bound_arret_axe)):
                    axes[i].axvspan(self.PlotsX[min(bound_arret_axe[p])],self.PlotsX[max(bound_arret_axe[p])], alpha=0.5, color='cyan',clip_on=True)   
       
        #Legend
        yellow_patch = mpatches.Patch(color='yellow', label='intern')
        blue_patch = mpatches.Patch(color='blue', label='extern')
        green_patch = mpatches.Patch(color='green', label='ebauche')
        cyan_patch = mpatches.Patch(color='cyan', label='arret axe')
        self.axsig.legend(handles=[yellow_patch,blue_patch,green_patch,cyan_patch], labels=('intern','extern','ebauche','arret axe',))

        
                    
    def rezoomPositions(self):
        # get current zoom limits from signal trace
        Tmin, Tmax = np.clip(self.axsig.get_xlim(), self.PlotsX.min(), self.PlotsX.max())
        # find nearest indexes for these limits
        iNearestTmin = self.PlotsX.sub(np.full(self.PlotsX.shape,Tmin)).abs().argmin()
        iNearestTmax = self.PlotsX.sub(np.full(self.PlotsX.shape,Tmax)).abs().argmin()
        # find maximum and minimum values in the interval to show
        iXmin = self.Raw['XPos'][iNearestTmin:iNearestTmax+1].argmin()
        iXmax = self.Raw['XPos'][iNearestTmin:iNearestTmax+1].argmax()
        iYmin = self.Raw['YPos'][iNearestTmin:iNearestTmax+1].argmin()
        iYmax = self.Raw['YPos'][iNearestTmin:iNearestTmax+1].argmax()
        # calculate display boudaries with margins
        bXmin = self.Raw['XPos'][iXmin] - (self.Raw['XPos'][iXmax]-self.Raw['XPos'][iXmin])*0.1
        bXmax = self.Raw['XPos'][iXmax] + (self.Raw['XPos'][iXmax]-self.Raw['XPos'][iXmin])*0.1
        bYmin = self.Raw['YPos'][iYmin] - (self.Raw['YPos'][iYmax]-self.Raw['YPos'][iYmin])*0.1
        bYmax = self.Raw['YPos'][iYmax] + (self.Raw['YPos'][iYmax]-self.Raw['YPos'][iYmin])*0.1
        # check and correct boudaries ratio at 2:1 to give enough ploting blank splace
        bmax = max((abs(bXmax-bXmin),abs(bYmax-bYmin)))
        if bXmax-bXmin < bmax:
            bXmax += bmax/4
            bXmin -= bmax/4
        if bYmax-bYmin < bmax:
            bYmax += bmax/4
            bYmin -= bmax/4
        # zoom positions
        self.axpos.set_xlim(bXmin, bXmax)
        self.axpos.set_ylim(bYmin, bYmax)
               

    def drawCursors(self):      
        if self.AbsAvailable: nabs = self.Raw['AbsCurv'][self.iNearest]
        if self.PosAvailable: 
            nx = self.Raw['XPos'][self.iNearest]
            ny = self.Raw['YPos'][self.iNearest]
        nval1 = self.Raw['Values1'][self.iNearest]
        nt = self.Raw['RelTime'][self.iNearest]

        self.message += '    Time=%.3f' %nt
        self.message += '    ' + self.Var1_name + '=%.3f' %nval1
        self.HdlSelSig.set_xdata([nt, nt])
        self.HdlSelSig.set_ydata([self.axsig.get_ylim()[0],self.axsig.get_ylim()[1]])
        self.HdlSel2.set_xdata([nt, nt])
        self.HdlSel2.set_ydata([self.ax2.get_ylim()[0],self.ax2.get_ylim()[1]])
        
        if self.Var2_name != '':
            nval2 = self.Raw['Values2'][self.iNearest]
            self.message += '    ' + self.Var2_name + '=%.3f' %nval2
            
        if self.PosAvailable: 
            self.message += '        Position : X=%.4f' %nx
            self.message += '    Y=%.4f' %ny
            self.HdlSelPos.set_xdata(nx)
            self.HdlSelPos.set_ydata(ny)
            
        if self.AbsAvailable: 
            self.message += '    Absissa=%.4f' %nabs

        if self.PlotMode == 1:
            self.HdlSel3.set_xdata([nt, nt])
            self.HdlSel3.set_ydata([self.ax3.get_ylim()[0],self.ax3.get_ylim()[1]])
            self.HdlSel4.set_xdata([nt, nt])
            self.HdlSel4.set_ydata([self.ax4.get_ylim()[0],self.ax4.get_ylim()[1]])

        self.HdlMessage.set_text(self.message)
        self.draw()
    
    
    def keyPressEvent(self,event):
        super(PlotCanvas, self).keyPressEvent(event)
        
        if self.disabled == False :
            if event.modifiers() & Qtc.Qt.ShiftModifier: # add factor to increment to go faster
                fac = 10
            else:
                fac = 1
            
            if event.key() == Qtc.Qt.Key_Right: # move cursors to next sample
                inc = 1*fac
                if self.iNearest < (len(self.Raw.values)-inc):
                    self.iNearest += inc
                    if self.PlotsX[self.iNearest] > self.axsig.get_xlim()[1]:
                        diff = self.PlotsX[self.iNearest] - self.axsig.get_xlim()[1]
                        self.axsig.set_xlim(self.axsig.get_xlim()[0]+diff,
                                            self.PlotsX[self.iNearest])
                    self.message = 'Moving %1d sample(s) forward' %inc 
                    if self.PosAvailable: self.rezoomPositions()
                    self.drawCursors()
                    
            if event.key() == Qtc.Qt.Key_Left: # move cursors to previous sample
                inc = 1*fac
                if self.iNearest >= inc:
                    self.iNearest -= inc
                    if self.PlotsX[self.iNearest] < self.axsig.get_xlim()[0]:
                        diff = self.axsig.get_xlim()[0] - self.PlotsX[self.iNearest]
                        self.axsig.set_xlim(self.PlotsX[self.iNearest],
                                            self.axsig.get_xlim()[1]-diff)
                    self.message = 'Moving %1d sample(s) backward' %inc
                    if self.PosAvailable: self.rezoomPositions()
                    self.drawCursors()
                    
            if event.key() == Qtc.Qt.Key_Up: # quick move cursors to next 50 samples
                inc = 50*fac
                if self.iNearest < (len(self.Raw.values)-inc):
                    self.iNearest += inc
                    if self.PlotsX[self.iNearest] > self.axsig.get_xlim()[1]:
                        diff = self.PlotsX[self.iNearest] - self.axsig.get_xlim()[1]
                        self.axsig.set_xlim(self.axsig.get_xlim()[0]+diff,
                                            self.PlotsX[self.iNearest])
                    self.message = 'Moving %1d samples forward' %inc
                    if self.PosAvailable: self.rezoomPositions()
                    self.drawCursors()
                    
            if event.key() == Qtc.Qt.Key_Down: # quick move cursors to previous 50 samples
                inc = 50*fac
                if self.iNearest >= inc:
                    self.iNearest -= inc
                    if self.PlotsX[self.iNearest] < self.axsig.get_xlim()[0]:
                        diff = self.axsig.get_xlim()[0] - self.PlotsX[self.iNearest]
                        self.axsig.set_xlim(self.PlotsX[self.iNearest],
                                            self.axsig.get_xlim()[1]-diff)
                    self.message = 'Moving %1d samples backward' %inc
                    if self.PosAvailable: self.rezoomPositions()
                    self.drawCursors()
                

    def mousePressEvent(self,event):
        super(PlotCanvas, self).mousePressEvent(event)
        
        if self.disabled == False and event.button() == Qtc.Qt.RightButton: # active on mouse right click only
            event.accept()
            m_x, m_y = event.x(), event.y()

            x, y = self.axsig.transData.inverted().transform([m_x, m_y])

            # chekc which plot was clicked on
            if x > self.axsig.get_xlim()[1] and self.PosAvailable : # click on positions map
                x, y = self.axpos.transData.inverted().transform([m_x, (self.get_width_height()[1]-m_y)])
                Point = pd.DataFrame()
                Point['X'] = [x]
                Point['Y'] = [y]
                Positions = self.Raw[['XPos','YPos']]
                self.iNearest = Positions.sub(np.full(Positions.shape,Point)).abs().sum(axis=1).argmin()
            else: # click on signal traces
                self.iNearest = self.PlotsX.sub(np.full(self.PlotsX.shape,x)).abs().argmin()
                if self.PosAvailable: self.rezoomPositions()

            self.message = 'Clicked on'
            self.drawCursors()
                
                
    def mouseDoubleClickEvent(self,event):
        if self.disabled == False:
            self.sig_DispSynchro.emit(True)

        


if __name__ == '__main__':
    
    # create a unique instance of app
    app = Qtc.QCoreApplication.instance()
    if app is None: # create application if app is not already opened
        app = Qtw.QApplication(sys.argv)
        
    ex = MainUI()
    exit
