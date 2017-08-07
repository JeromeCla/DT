
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
from matplotlib.ticker import FormatStrFormatter
import base64

class MainUI(Qtw.QDialog):
 
    def __init__(self, parent=None):
        
        # set form as parent entity, add Minimize, Maximize and Close buttons
        super().__init__(parent,
             flags=Qtc.Qt.WindowMaximizeButtonHint|Qtc.Qt.WindowMinimizeButtonHint|Qtc.Qt.WindowCloseButtonHint)
        
        self.title = 'CSV Tracer Mapper'
        self.version = 'v1.02'
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
        self.DefaultPath = 'E:/GFMS/Data/2017-06 - WEDM Process Analytics/1 - CSV conversion/'
        
        self.VarTime = 'Time'
        self.VarAbs = 'MainGeom_AbsCurTot_mm'
        self.Var1 = ''
        self.VarXPos = 'TkEd_pCM_Regle_X'
        self.VarYPos = 'TkEd_pCM_Regle_Y'
        self.VarStrat1 = 'Stra_Etat_TableActive'
        self.VarStrat2 = 'Stra_ModifCROV_Final'
        
        self.MovingWindow = 125 # number of samples for moving calculations (! should be impair to avoid aliasing)
        self.FirstExecution = True
        self.LoadOnlyVar = False
        self.StratsAvailable = False
        self.synchroInterval = 500
        self.progressPieChars = ['\u25CB','\u25D4','\u25D1','\u25D5','\u25CF']
        
        self.popupInfo()
 
    def popupInfo(self):
        msg = Qtw.QMessageBox()
        # set +GF+ logo embedded in base64 encoding
        b64_data = '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'
        pm = Qtg.QPixmap()
        pm.loadFromData(base64.b64decode(b64_data))
        msg.setIconPixmap(pm)
#        msg.setIcon(Qtw.QMessageBox.Information)
        msg.setWindowTitle(self.title + ' ' + self.version)
        msg.setWindowFlags(Qtc.Qt.WindowStaysOnTopHint)
        msg.setText('Trace and map positions of CSV files from EDM machines')
        msg.setInformativeText('Written by ' + self.author + '\n' +\
                               self.copyright)
#        msg.setDetailedText("The details are as follows...")
        msg.setStandardButtons(Qtw.QMessageBox.Ok|Qtw.QMessageBox.Cancel)
        msg.buttonClicked.connect(self.popupClick)
        
        msg.show()
        msg.exec_()
        
    def popupClick(self,btn):
        if btn.text() == 'Cancel':
            # Quit application
            self.close()
        else:
            # Continue
            self.initWidgets()
            self.selectDir()
    
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
        
        self.lbFileName = Qtw.QLabel('Aquisition File :')
        self.lbFileName.setFont(Qtg.QFont('SansSerif', 10))
        self.lbFileName.setAlignment(Qtc.Qt.AlignRight|Qtc.Qt.AlignVCenter)
        dflayout.addWidget(self.lbFileName,1)
           
        self.cbFileName = Qtw.QComboBox(self)
        self.cbFileName.setFont(Qtg.QFont('SansSerif', 10))
        self.cbFileName.activated[str].connect(self.onSelFile)
        self.cbFileName.setMaxVisibleItems(30)
        dflayout.addWidget(self.cbFileName,3)
        
        self.lbSignal1 = Qtw.QLabel('Signal 1:')
        self.lbSignal1.setFont(Qtg.QFont('SansSerif', 10))
        self.lbSignal1.setAlignment(Qtc.Qt.AlignRight|Qtc.Qt.AlignVCenter)
        dflayout.addWidget(self.lbSignal1,1)
        
        self.cbSignal1 = Qtw.QComboBox(self)
        self.cbSignal1.setFont(Qtg.QFont('SansSerif', 10))
        self.cbSignal1.activated[str].connect(self.onSelSignal1)
        self.cbSignal1.setMaxVisibleItems(30)
        dflayout.addWidget(self.cbSignal1,3)

        self.cbOperator1 = Qtw.QComboBox(self)
        self.cbOperator1.setFont(Qtg.QFont('SansSerif', 10, weight=Qtg.QFont.Bold))
        self.cbOperator1.setStyleSheet('color: #008000')
        self.cbOperator1.activated[str].connect(self.onSelOperator)
        self.cbOperator1.addItems([' ', '+', '-', 'x', '/'])
        self.cbOperator1.setFixedWidth(35)
        self.cbOperator1.setDisabled(True)
        self.cbOperator1.setToolTip('Operator for Signal 2 :\n\n' + \
                                '(empty) Signals 1 and 2 are independant\n' + \
                                '\"+\" add Signal 2 to Signal 1\n' + \
                                '\"-\" substract Signal 2 to Signal 1\n' + \
                                '\"x\" multiply Signal 2 to Signal 1\n' + \
                                '\"/\" divide Signal 2 to Signal 1')
        self.cbOperator1.setCurrentIndex(0)
        dflayout.addWidget(self.cbOperator1,0)
        
        self.lbSignal2 = Qtw.QLabel('Signal 2:')
        self.lbSignal2.setFont(Qtg.QFont('SansSerif', 10))
        self.lbSignal2.setAlignment(Qtc.Qt.AlignRight|Qtc.Qt.AlignVCenter)
        dflayout.addWidget(self.lbSignal2,1)
        
        self.cbSignal2 = Qtw.QComboBox(self)
        self.cbSignal2.setFont(Qtg.QFont('SansSerif', 10))
        self.cbSignal2.activated[str].connect(self.onSelSignal2)
        self.cbSignal2.setMaxVisibleItems(30)
        dflayout.addWidget(self.cbSignal2,3)
        
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
        
        dflayout.addWidget(self.btReload,2)
        
        self.gbDataFile.setLayout(dflayout)
        ctllayout.addWidget(self.gbDataFile,10)
                       
        self.gbDispMode = Qtw.QGroupBox('Display mode')
        self.gbDispMode.setContentsMargins(0,6,0,0)
        self.gbDispMode.setAlignment(Qtc.Qt.AlignCenter|Qtc.Qt.AlignVCenter)
        dmlayout = Qtw.QHBoxLayout()
        
        self.rbDispMode = Qtw.QRadioButton('Traces')
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

        self.ckDispStrats = Qtw.QCheckBox('Strategies')
        self.ckDispStrats.setFont(Qtg.QFont('SansSerif', 10))
        self.ckDispStrats.toggled.connect(self.onDispStrategies)
        self.ckDispStrats.setChecked(False)
        self.ckDispStrats.setHidden(True)
        dmlayout.addWidget(self.ckDispStrats,1)
        
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

        # Set layout
        ctlwidget = Qtw.QWidget(self)
        ctlwidget.setLayout(ctllayout)
        
        layout = Qtw.QVBoxLayout()
        layout.setContentsMargins(2,2,2,0)
        layout.addWidget(ctlwidget,0)
        layout.addWidget(self.canvas,1)
        
        self.setLayout(layout)
        
        self.gbDispMode.setDisabled(True)
        self.gbNav.setDisabled(True)
        
#        self.show()
        self.showMaximized()
        
    def selectDir(self):
        self.Datadir = str(Qtw.QFileDialog.getExistingDirectory\
                           (self,
                            "Select Directory for CSV data files",
                            self.DefaultPath)) + '/'
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
        self.canvas.clearZoomContext()
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
                
                self.canvas.saveZoomContext()
                
                if self.rbDispMode.Mode == 1: # Statistics mode selected
                    self.CalculateStats() # Statistics mode selected : calculate data
                    self.canvas.message = 'Displaying statistics... '
                
                elif self.rbDispMode.Mode == 2: # Spectrogram mode selected
                    self.canvas.message = 'Displaying spectrogram... '
                    
#                elif self.rbDispMode.Mode == 3 :
#                    self.loadBatches() # Load all batches of the same pass
                    
                else: # direct signals mode
                    self.canvas.message = 'Displaying traces... '
        
                self.canvas.showMessage()
                self.repaint()
                self.canvas.redraw()
                self.canvas.restoreZoomContext(newVar=False)
            
        self.canvas.setFocus()
                    
    def onDispStrategies(self):
        # Toggle strategies highlights and symbols
        self.canvas.saveZoomContext()
        if self.ckDispStrats.isChecked():
            self.canvas.message = 'Overlapping strategies... '
            self.canvas.DrawStrats = True
        else:
            self.canvas.message = 'Clearing strategies... '
            self.canvas.DrawStrats = False
            
        self.canvas.showMessage()
        self.repaint()
        
        self.canvas.message = 'Ready'
        self.canvas.redraw()
        self.canvas.restoreZoomContext(newVar=False)
        self.canvas.setFocus()
            
#    def onAbsModeChange(self):
#        self.canvas.AbsCurvMode = self.ckAbsMode.isChecked()


    # DISP SYNCHRO
    
    def onDispSynchro(self):

        return
#        if self.canvas.SynchroMode == False:
#            self.canvas.SynchroMode = True
#            self.canvas.message = 'Please wait for data synchronization of all .csv files in directory...'
#            self.disableControls()
#            self.canvas.showDisable()
#            self.repaint()
#            
#            # Load synchronized plots on the same position
#            self.canvas.dataLoaded = False
#            inc = 0
#            for file in self.FilesList:
#  
#                self.canvas.message = 'Synchronizing data file %1d' %(inc+1) + \
#                ' of ' + str(len(self.FilesList)) + ' : \"' + file + '\"... '               
#                self.canvas.showMessage()
#                self.repaint()
#                
#                # clear import frame
#                csvdata = pd.DataFrame()
#                # prepare list of variables
#                VarList = [self.Var1, self.VarXPos, self.VarYPos]
#                rowsSkipped = self.canvas.iNearest - self.synchroInterval
#                rowsLoaded = 2*self.synchroInterval
#                
#                # Open CSV file of a real data set
#                with open(self.Datadir + file, mode='r', encoding='utf-8') as csvfile:
#                    csvdata = pd.read_csv(csvfile,
#                                          sep=';',
#                                          dtype=str,
#                                          usecols=VarList,
#                                          skiprows=rowsSkipped,
#                                          nrows=rowsLoaded)
#
#                self.canvas.Synch[inc] = csvdata[self.Var1].astype(np.float)
#                
#                inc += 1 
##                time.sleep(0.25)
#            
#            self.canvas.dataLoaded = True
#            self.canvas.message = 'Double-click to go back to signal'
#            self.canvas.redraw()
#            
#        else:
#            self.canvas.SynchroMode = False
#            self.enableControls()
#            self.onReloadData()
#            
#        self.canvas.setFocus()



    def loadFilesList(self):
        self.cbFileName.clear()
        self.FilesList.clear()
        os.chdir(self.Datadir)
        for file in glob.glob('*.csv'):
            self.FilesList += [file]
        self.cbFileName.addItems(self.FilesList)
        if len(self.FilesList) > 0:
            self.canvas.message = 'Please select acquisition file from the list... '
            self.canvas.showDisable()
            self.cbFileName.showPopup()
        else:
            self.canvas.message = 'ERROR : No CSV file vailable, please check directory... '
            self.canvas.showDisable()
        
        
    def onSelFile(self, text):
        self.canvas.message = 'Please wait for preparation of the list of signals from \"' + text + '\"...'
        self.canvas.showDisable()

        self.Filename = self.cbFileName.currentText()
        self.loadSignalsList()
        if self.canvas.dataLoaded and self.SignalsList != []:
            self.btReload.setHidden(False)
        self.canvas.dataLoaded = False
        self.LoadOnlyVar = False

    def loadSignalsList(self):
        # Open CSV file of a real data set to import columns (header) names
        with open(self.Datadir + self.Filename, mode='r', encoding='utf-8') as csvfile:
            csvdata = pd.read_csv(csvfile, sep=';', dtype=str, nrows=1).columns
        if len(csvdata) > 1:
            self.SignalsList = csvdata.tolist()
            self.canvas.message = 'Please select signal form the list and click \"Reload Data\"...'
            
            CurSignal1 = self.cbSignal1.currentText()
            self.cbSignal1.clear()
#            self.cbSignal1.addItems(self.SignalsList)
            self.cbSignal1.addItems(['%03d' %(self.SignalsList.index(elt)+1) + ' ' + elt for elt in self.SignalsList])
            IndSignal1 = self.cbSignal1.findText(CurSignal1)
            if IndSignal1 > 0:
                self.cbSignal1.setCurrentIndex(IndSignal1)
    
            CurSignal2 = self.cbSignal2.currentText()
            self.cbSignal2.clear()
            self.cbSignal2.addItems(['000 (no signal)'] +\
                                    ['%03d' %(self.SignalsList.index(elt)+1) + ' ' + elt for elt in self.SignalsList])
            IndSignal2 = self.cbSignal1.findText(CurSignal2)
            if IndSignal2 > 0:
                self.cbSignal2.setCurrentIndex(IndSignal2)
                
            if self.FirstExecution: # quick select signal on the first execution of the program
                self.cbSignal1.showPopup()
                self.FirstExecution = False
            
        else:
            self.SignalsList = []
            self.canvas.message = 'ERROR : Selected file does not have enougth data !'
            
            self.cbSignal1.clear()
            self.cbSignal2.clear()
            
        self.canvas.showMessage()
        
    def onSelSignal1(self, text):
        self.canvas.message = '\"' + text + '\" signal selected, please click on \"Reload Data\" to refresh...'
        self.canvas.showDisable()
        self.Var1 = self.cbSignal1.currentText()[4:]
        self.Var2 = self.cbSignal2.currentText()[4:]
        self.btReload.setHidden(False)
            
    def onSelSignal2(self, text):
        if text == '(no signal)':
            self.cbOperator1.setCurrentIndex(0)
            self.cbOperator1.setDisabled(True)
        else:
            self.cbOperator1.setDisabled(False)
            self.canvas.message = '\"' + text + '\" signal selected, please click on \"Reload Data\" to refresh...'
            self.canvas.showDisable()
            self.btReload.setHidden(False)
        self.Var1 = self.cbSignal1.currentText()[4:]
        self.Var2 = self.cbSignal2.currentText()[4:]
        
    def onSelOperator(self):
        if self.canvas.dataLoaded:
            self.canvas.message = 'operator changed, please click on \"Reload Data\" to refresh...'
            self.canvas.showDisable()
            self.btReload.setHidden(False)
        
    def onReloadData(self):
        self.btReload.setHidden(True)
        self.canvas.dataLoaded = False
        
        self.canvas.showDisable()
        
        if self.LoadOnlyVar == False: # change file / data set
            
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

            if {self.VarStrat1}.issubset(self.SignalsList)\
            & {self.VarStrat2}.issubset(self.SignalsList): # strategic transcient phases for wire EDM
                VarList += [self.VarStrat1, self.VarStrat2]
                self.StratsAvailable = True
                self.ckDispStrats.setHidden(False)
            else:
                self.StratsAvailable = False
                self.ckDispStrats.setHidden(True)

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
                self.canvas.message = msg + '\n' + self.progressPieChars[np.clip(progress,0,4)]
                self.canvas.showMessage()
                self.repaint()
                csvdata = pd.DataFrame.append(csvdata,chunk)
                progress +=1
                
                
            # convert values into floats
            self.canvas.Raw['Time'] = csvdata[self.VarTime].astype(np.float)
            
            if self.canvas.AbsAvailable: self.canvas.Raw['AbsCurv'] = csvdata[self.VarAbs].astype(np.float)
            
            self.canvas.Raw['Values1'] = csvdata[self.Var1].astype(np.float)
            
            self.canvas.Sgn2Available = False
            if self.Var2 != '(no signal)':      
                self.canvas.Raw['Values2'] = csvdata[self.Var2].astype(np.float)
                self.canvas.Var2_name = self.Var2
                if self.cbOperator1.currentText() == '+': 
                    self.canvas.Raw['Values1'] = self.canvas.Raw['Values1'].add(self.canvas.Raw['Values2'])
                    self.canvas.Var1_name = self.Var1 + ' + ' + self.Var2
                elif self.cbOperator1.currentText() == '-':
                    self.canvas.Raw['Values1'] = self.canvas.Raw['Values1'].sub(self.canvas.Raw['Values2'])
                    self.canvas.Var1_name = self.Var1 + ' - ' + self.Var2
                elif self.cbOperator1.currentText() == 'x':
                    self.canvas.Raw['Values1'] = self.canvas.Raw['Values1'].mul(self.canvas.Raw['Values2'])
                    self.canvas.Var1_name = self.Var1 + ' x ' + self.Var2
                elif self.cbOperator1.currentText() == '/':
                    self.canvas.Raw['Values1'] = self.canvas.Raw['Values1'].div(self.canvas.Raw['Values2'])
                    self.canvas.Var1_name = self.Var1 + ' / ' + self.Var2
                else:
                    self.canvas.Var1_name = self.Var1
                    self.canvas.Sgn2Available = True
            else:
                self.canvas.Var1_name = self.Var1
                self.canvas.Var2_name = '' # no name will diseable signal
                            
            if self.StratsAvailable:
                self.canvas.Raw['Strat1'] = csvdata[self.VarStrat1].astype(np.float)
                self.canvas.Raw['Strat2'] = csvdata[self.VarStrat2].astype(np.float)
                # Axes stop
                indexes1 = np.where(self.canvas.Raw['Strat1'].div(10000).round(0) == 6.0)[0]
                # Roungh cut
                indexes2 = np.where(self.canvas.Raw['Strat1'].div(10000).round(0) == 5.0)[0]
                # Internal curve
                indexes3 = np.concatenate((np.where(self.canvas.Raw['Strat1'].div(10000).round(0) == 7.0)[0],
                                           np.where(self.canvas.Raw['Strat2'] < 1.0)[0]))
                # External curve
                indexes4 = np.concatenate((np.where(self.canvas.Raw['Strat1'].div(10000).round(0) == 8.0)[0],
                                           np.where(self.canvas.Raw['Strat2'] > 1.0)[0]))
                # generate strategy markers
                self.canvas.Raw['SigStrat1'] = np.full(self.canvas.Raw['Values1'].shape,np.nan)
                self.canvas.Raw['SigStrat1'][indexes1] = self.canvas.Raw['Values1'][indexes1]
                self.canvas.Raw['SigStrat2'] = np.full(self.canvas.Raw['Values1'].shape,np.nan)
                self.canvas.Raw['SigStrat2'][indexes2] = self.canvas.Raw['Values1'][indexes2]
                self.canvas.Raw['SigStrat3'] = np.full(self.canvas.Raw['Values1'].shape,np.nan)
                self.canvas.Raw['SigStrat3'][indexes3] = self.canvas.Raw['Values1'][indexes3]
                self.canvas.Raw['SigStrat4'] = np.full(self.canvas.Raw['Values1'].shape,np.nan)
                self.canvas.Raw['SigStrat4'][indexes4] = self.canvas.Raw['Values1'][indexes4]
                # drop unused temporary columns
                self.canvas.Raw.drop(['Strat1', 'Strat2'],1,inplace=True)
                # set names for display
                self.canvas.Strat1_name = 'Axes stop'
                self.canvas.Strat2_name = 'Roungh cut'
                self.canvas.Strat3_name = 'Internal curve'
                self.canvas.Strat4_name = 'External curve'
                
            if self.canvas.PosAvailable:
                self.canvas.Raw['XPos'] = csvdata[self.VarXPos].astype(np.float)
                self.canvas.Raw['YPos'] = csvdata[self.VarYPos].astype(np.float)
                if self.StratsAvailable: # include strategy markers if any
                    self.canvas.Raw['XPosStrat1'] = np.full(self.canvas.Raw['XPos'].shape,np.nan)
                    self.canvas.Raw['YPosStrat1'] = np.full(self.canvas.Raw['YPos'].shape,np.nan)
                    self.canvas.Raw['XPosStrat1'][indexes1] = self.canvas.Raw['XPos'][indexes1]
                    self.canvas.Raw['YPosStrat1'][indexes1] = self.canvas.Raw['YPos'][indexes1]
                    self.canvas.Raw['XPosStrat2'] = np.full(self.canvas.Raw['XPos'].shape,np.nan)
                    self.canvas.Raw['YPosStrat2'] = np.full(self.canvas.Raw['YPos'].shape,np.nan)
                    self.canvas.Raw['XPosStrat2'][indexes2] = self.canvas.Raw['XPos'][indexes2]
                    self.canvas.Raw['YPosStrat2'][indexes2] = self.canvas.Raw['YPos'][indexes2]
                    self.canvas.Raw['XPosStrat3'] = np.full(self.canvas.Raw['XPos'].shape,np.nan)
                    self.canvas.Raw['YPosStrat3'] = np.full(self.canvas.Raw['YPos'].shape,np.nan)
                    self.canvas.Raw['XPosStrat3'][indexes3] = self.canvas.Raw['XPos'][indexes3]
                    self.canvas.Raw['YPosStrat3'][indexes3] = self.canvas.Raw['YPos'][indexes3]
                    self.canvas.Raw['XPosStrat4'] = np.full(self.canvas.Raw['XPos'].shape,np.nan)
                    self.canvas.Raw['YPosStrat4'] = np.full(self.canvas.Raw['YPos'].shape,np.nan)
                    self.canvas.Raw['XPosStrat4'][indexes4] = self.canvas.Raw['XPos'][indexes4]
                    self.canvas.Raw['YPosStrat4'][indexes4] = self.canvas.Raw['YPos'][indexes4]
            
            # cacluate relative and delta times
            self.canvas.Raw['RelTime'] = self.canvas.Raw['Time'].sub(self.canvas.Raw['Time'][0])
            self.canvas.Raw['dTime'] = self.canvas.Raw['Time'].sub(self.canvas.Raw['Time'].shift(1)).fillna(0)
            
#            print('Done !')
            
            # display information on data imported
            print('Trace is %d samples long ' % len(csvdata.values), end='')
            print('(%.3f ' % (self.canvas.Raw['RelTime'].values[-1] - self.canvas.Raw['RelTime'].values[0]), end = '')
            print(self.VarAbs + ')')
                 
        else: # load only variables form the same file
            
            # reset statistics
            self.canvas.Stats = pd.DataFrame()
            
            msg = 'Please wait for loading variable(s) from file \"' + self.Filename + '\"...'
            self.canvas.message = msg
            self.canvas.showMessage()
            self.repaint()
            
            # Prepare variables list
            VarList = [self.Var1]
            
            if self.StratsAvailable:
                VarList += [self.VarStrat1, self.VarStrat2]
            
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
            
            self.canvas.Sgn2Available = False
            if self.Var2 != '(no signal)':
                self.canvas.Raw['Values2'] = csvdata[self.Var2].astype(np.float)
                self.canvas.Var2_name = self.Var2
                if self.cbOperator1.currentText() == '+': 
                    self.canvas.Raw['Values1'] = self.canvas.Raw['Values1'].add(self.canvas.Raw['Values2'])
                    self.canvas.Var1_name = self.Var1 + ' + ' + self.Var2
                elif self.cbOperator1.currentText() == '-':
                    self.canvas.Raw['Values1'] = self.canvas.Raw['Values1'].sub(self.canvas.Raw['Values2'])
                    self.canvas.Var1_name = self.Var1 + ' - ' + self.Var2
                elif self.cbOperator1.currentText() == 'x':
                    self.canvas.Raw['Values1'] = self.canvas.Raw['Values1'].mul(self.canvas.Raw['Values2'])
                    self.canvas.Var1_name = self.Var1 + ' x ' + self.Var2
                elif self.cbOperator1.currentText() == '/':
                    self.canvas.Raw['Values1'] = self.canvas.Raw['Values1'].div(self.canvas.Raw['Values2'])
                    self.canvas.Var1_name = self.Var1 + ' / ' + self.Var2
                else:
                    self.canvas.Sgn2Available = True
                    self.canvas.Var1_name = self.Var1
            else:
                self.canvas.Var1_name = self.Var1
                self.canvas.Var2_name = '' # no name will diseable signal
            
            if self.StratsAvailable:
                self.canvas.Raw['Strat1'] = csvdata[self.VarStrat1].astype(np.float)
                self.canvas.Raw['Strat2'] = csvdata[self.VarStrat2].astype(np.float)
                # Axes stop
                indexes1 = np.where(self.canvas.Raw['Strat1'].div(10000).round(0) == 6.0)[0]
                # Roungh cut
                indexes2 = np.where(self.canvas.Raw['Strat1'].div(10000).round(0) == 5.0)[0]
                # Internal curve
                indexes3 = np.concatenate((np.where(self.canvas.Raw['Strat1'].div(10000).round(0) == 7.0)[0],
                                           np.where(self.canvas.Raw['Strat2'] < 1.0)[0]))
                # External curve
                indexes4 = np.concatenate((np.where(self.canvas.Raw['Strat1'].div(10000).round(0) == 8.0)[0],
                                           np.where(self.canvas.Raw['Strat2'] > 1.0)[0]))
                # generate strategy markers
                self.canvas.Raw['SigStrat1'] = np.full(self.canvas.Raw['Values1'].shape,np.nan)
                self.canvas.Raw['SigStrat1'][indexes1] = self.canvas.Raw['Values1'][indexes1]
                self.canvas.Raw['SigStrat2'] = np.full(self.canvas.Raw['Values1'].shape,np.nan)
                self.canvas.Raw['SigStrat2'][indexes2] = self.canvas.Raw['Values1'][indexes2]
                self.canvas.Raw['SigStrat3'] = np.full(self.canvas.Raw['Values1'].shape,np.nan)
                self.canvas.Raw['SigStrat3'][indexes3] = self.canvas.Raw['Values1'][indexes3]
                self.canvas.Raw['SigStrat4'] = np.full(self.canvas.Raw['Values1'].shape,np.nan)
                self.canvas.Raw['SigStrat4'][indexes4] = self.canvas.Raw['Values1'][indexes4]
                # drop unused temporary columns
                self.canvas.Raw.drop(['Strat1', 'Strat2'],1,inplace=True)            
            
        # check moving window length
        if self.MovingWindow > (len(self.canvas.Raw['Values1'].values)):
            self.canvas.message = 'ERROR : MovingWindow value is bigger than data length'
            self.canvas.showMessage()
            return
        else:
            self.canvas.dataLoaded = True # data are loaded
            self.canvas.filename = self.cbFileName.currentText()
            
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
                self.canvas.redraw()
            else:
                self.canvas.message = 'Ready'
                self.canvas.showMessage()
        
        # sucess : refresh and enable displays
        self.enableControls()
        self.rbDispMode.setDisabled(False)

        if self.LoadOnlyVar: self.canvas.saveZoomContext()
        self.canvas.redraw()
        if self.LoadOnlyVar: self.canvas.restoreZoomContext(newVar=True)
        self.LoadOnlyVar = True
        
        self.canvas.setFocus()
        
        
    def CalculateStats(self):
        # CALUCULATE STATISTICS
        if self.canvas.Stats.empty:
            
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
        self.repaint()



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
        
        self.Var1_name = ''
        self.Var2_name = ''
        self.Var1_units = ''
        self.Var2_units = ''
        self.Abs_name = ''
        self.Abs_units = ''
        self.XPos_name = ''
        self.YPos_name = ''
        self.Pos_units = ''
        self.Strat1_name = ''
        self.Strat2_name = ''
        self.Strat3_name = ''
        self.Strat4_name = ''
        
        self.message = ''
        self.HdlMessage = None
        self.filename = ''
        self.PlotMode = 0
        self.AbsCurvMode = False
        self.dataLoaded = False
        self.Fs = 2 # default sampling frequency
        self.iNearest = 0
        self.SynchroMode = False
        self.AbsAvailable = False
        self.PosAvailable = False
        self.Sgn2Available = False
        self.DrawStrats = False
        self.disabled = False
        
        self.ZoomContext = {'1x':0, '1X':0, '1y':0, '1Y':0,
                            'posx':0, 'posX':0, 'posy':0, 'posY':0}
        
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

            #Check if positions map will to be plotted, make free space if so
            if self.PosAvailable: 
                tracesWidth = 0.50
            else:
                tracesWidth = 0.80
                
            # Plot 1 : direct signal
            self.axsig = self.fig.add_axes([0.08, 0.70, tracesWidth, 0.20])
            self.axsig.clear()
            self.axsig.grid(color='#DDDDDD',linestyle=':')
            self.axsig.set_title('Statistics on \"' + self.Var1_name + '\" variable')
            if self.DrawStrats: self.drawSigStratsHighlights() # strategies highlight
            self.axsig.plot(self.PlotsX, self.Raw['Values1'], color='#0000A0', label=self.Var1_name + ' [' + self.Var1_units + ']')
            if self.DrawStrats: self.drawSigStratsSymbols() # strategies symbols overlay
            self.axsig.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL', prop={'size':8})
            
            # Plot 2 : Tracking signals
            self.ax2 = self.fig.add_axes([0.08, 0.49, tracesWidth, 0.20], sharex=self.axsig)
            self.ax2.clear()
            self.ax2.grid(color='#DDDDDD',linestyle=':')
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
            self.ax3.xaxis.grid(color='#DDDDDD', linestyle=':')
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
            self.ax4.xaxis.grid(color='#DDDDDD', linestyle=':')
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
            
        elif self.PlotMode == 2: # SPECTROGRAM
        
            #Check if position have to be plotted
            if self.PosAvailable: 
                tracesWidth = 0.50
            else:
                tracesWidth = 0.80    
        
            # Plot 1 : direct signal
            self.axsig = self.fig.add_axes([0.1, 0.51, tracesWidth, 0.40])
            self.axsig.clear()
            self.axsig.grid(color='#DDDDDD',linestyle=':')
            self.axsig.set_title('Spectrogram of \"' + self.Var1_name + '\" variable')
            if self.DrawStrats: self.drawSigStratsHighlights() # strategies highlight
            self.axsig.plot(self.PlotsX, self.Raw['Values1'], color='#0000A0', label=self.Var1_name + ' [' + self.Var1_units + ']')
            if self.DrawStrats: self.drawSigStratsSymbols() # strategies symbols overlay
            self.axsig.legend(bbox_to_anchor=(1, 0.5), loc=6, title='DIRECT SIGNAL', prop={'size':8})
 
#                self.plt.setp([axsig.get_xticklabels() for a in self.fig.axes[:-1]], visible=False)
            
            # Plot 2 : Spectrogram
            self.ax2 = self.fig.add_axes([0.1, 0.1, tracesWidth, 0.40], sharex=self.axsig)
            self.ax2.clear()
            self.ax2.set_yscale('symlog', subsy=np.linspace(1,10,10)[1:-1])
            self.ax2.get_yaxis().set_major_formatter(FormatStrFormatter('%1.0f'))
            self.ax2.tick_params(axis='y', which='major', right='on')
            self.ax2.tick_params(axis='y', which='minor', right='on')
            #Calculate sampling rate from calculated deltatime
            self.Fs = 1/self.Raw['dTime'][1]
            # activate image interpolation
            plt.rcParams['image.interpolation'] = 'hanning'
            plt.rcParams['image.resample'] = False
            spec_p, spec_frqs, spec_bins, spec_im = self.ax2.specgram(self.Raw['Values1'],
                                                                      window = mlab.window_hanning,
                                                                      NFFT = 1024,
                                                                      Fs = self.Fs,
                                                                      noverlap = 0,
                                                                      mode='psd', 
                                                                      scale='dB',
                                                                      detrend='mean',
                                                                      cmap='Greys') # cmap can be 'Greys' 'plasma' 'viridis' 'gnuplot2'
            
            self.ax2.set_ylabel('Frequency [Hz]')
            self.ax2.set_xlabel(self.Abs_name + ' [' + self.Abs_units + ']')
            
            # spectrum color bar
            self.ax3 = self.fig.add_axes([0.11+tracesWidth, 0.1, 0.01, 0.40])
            self.fig.colorbar(label='dB', mappable=spec_im, cax=self.ax3)
            
            # cursor line on signal trace
            self.HdlSel2, = self.ax2.plot([self.PlotsX[self.iNearest],
                                           self.PlotsX[self.iNearest]],
                                          [self.ax2.get_ylim()[0],
                                           self.ax2.get_ylim()[1]],
                                           color='#FF0000', alpha=0.7)
            
        else : # TRACES
        
            #Check for display space disponibilities
            if self.PosAvailable: 
                tracesWidth = 0.57
            else:
                tracesWidth = 0.90
        
            # Plot 1 : Signal 1
            if self.Sgn2Available:
                self.axsig = self.fig.add_axes([0.08, 0.51, tracesWidth, 0.40])
            else:
                self.axsig = self.fig.add_axes([0.08, 0.1, tracesWidth, 0.80])
            self.axsig.clear()
            self.axsig.grid(color='#DDDDDD',linestyle=':')         
            if self.DrawStrats: self.drawSigStratsHighlights() # strategies highlight
            self.axsig.plot(self.PlotsX, self.Raw['Values1'],
                            color='#0000A0', label=self.Var1_name + ' [' + self.Var1_units + ']') # trace for signal 1
            if self.DrawStrats: self.drawSigStratsSymbols() # strategies symbols overlay
            self.axsig.set_ylabel(self.Var1_name + ' [' + self.Var1_units + ']')
            
            if self.Sgn2Available :
                # Plot 2 : direct signal 2 (if any)
                self.ax2 = self.fig.add_axes([0.08, 0.1, tracesWidth, 0.40], sharex=self.axsig)
                self.ax2.clear()
                self.ax2.grid(color='#DDDDDD',linestyle=':')
                self.ax2.plot(self.PlotsX, self.Raw['Values2'], color='#00A000', label=self.Var2_name + ' [' + self.Var2_units + ']')
                self.ax2.set_ylabel(self.Var2_name + ' [' + self.Var2_units + ']')
                
                # abcissa title for second plot
                self.ax2.set_xlabel(self.Abs_name + ' [' + self.Abs_units + ']')
            
                # cursor line on signal trace
                self.HdlSel2, = self.ax2.plot([self.PlotsX[self.iNearest],
                                               self.PlotsX[self.iNearest]],
                                              [self.ax2.get_ylim()[0],
                                               self.ax2.get_ylim()[1]],
                                               color='#FF0000', alpha=0.5)
            else:
                # abcissa title for signle plot
                self.axsig.set_xlabel(self.Abs_name + ' [' + self.Abs_units + ']')
    
    
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
            self.axpos.grid(color='#DDDDDD',linestyle=':')
            if self.DrawStrats: self.drawPosStratsHighlights() # strategies highlight
            self.axpos.plot(self.Raw['XPos'], self.Raw['YPos'], color='#0000A0') # trace for positions
            if self.DrawStrats: self.drawPosStratsSymbols() # strategies symbols overlay 
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
                      color='#808080', alpha=0.3)
            # trace ending arrow
            arr_dir_X = (self.Raw['XPos'].values[-1] - self.Raw['XPos'].values[-(dir_len+1)])/dir_len
            arr_dir_Y = (self.Raw['YPos'].values[-1] - self.Raw['YPos'].values[-(dir_len+1)])/dir_len
            self.axpos.arrow(self.Raw['XPos'].values[-1], self.Raw['YPos'].values[-1], arr_dir_X, arr_dir_Y, 
                      head_width=head_width_set, head_length=head_length_set, 
                      color='#808080', alpha=0.3)
        
            # Make subplots close to each other and hide x ticks for all but bottom plot
            self.fig.subplots_adjust(hspace=0.05, wspace=0.05)
            
            # cursor dot on positions map
            self.HdlSelPos, = self.axpos.plot(self.Raw['XPos'][self.iNearest],
                                              self.Raw['YPos'][self.iNearest],
                                              marker="o", color='#FF0000', alpha=0.5)
            
        self.draw()
        
    def drawSigStratsHighlights(self):
        self.axsig.plot(self.PlotsX, self.Raw['SigStrat2'], 
                        label=self.Strat2_name, color='#FF8000', linewidth=8, alpha=0.5)
        self.axsig.plot(self.PlotsX, self.Raw['SigStrat3'],
                        label=self.Strat3_name, color='#00FF00', linewidth=8, alpha=0.5)
        self.axsig.plot(self.PlotsX, self.Raw['SigStrat4'],
                        label=self.Strat4_name, color='#8000FF', linewidth=8, alpha=0.5)
    
    def drawSigStratsSymbols(self):
        self.axsig.plot(self.PlotsX, self.Raw['SigStrat1'],
                        label=self.Strat1_name, color='#FF0000',
                        marker='x', markeredgewidth=3, markersize=12,
                        alpha=0.5)
        self.axsig.legend(loc=1, title='STRATEGIES', prop={'size':8})
#        self.axsig.legend() # very slow !!
        
    def drawPosStratsHighlights(self):
        self.axpos.plot(self.Raw['XPosStrat2'], self.Raw['YPosStrat2'], 
                        label=self.Strat2_name, color='#FF8000', linewidth=8, alpha=0.5)
        self.axpos.plot(self.Raw['XPosStrat3'], self.Raw['YPosStrat3'],
                        label=self.Strat3_name, color='#00FF00', linewidth=8, alpha=0.5)
        self.axpos.plot(self.Raw['XPosStrat4'], self.Raw['YPosStrat4'],
                        label=self.Strat4_name, color='#8000FF', linewidth=8, alpha=0.5)
    
    def drawPosStratsSymbols(self):
        self.axpos.plot(self.Raw['XPosStrat1'], self.Raw['YPosStrat1'],
                        label=self.Strat1_name, color='#FF0000',
                        marker='x', markeredgewidth=3, markersize=12,
                        alpha=0.5)     
        
    def saveZoomContext(self):
        self.ZoomContext['1x'], self.ZoomContext['1X'] = self.axsig.get_xlim()
        self.ZoomContext['1y'], self.ZoomContext['1Y'] = self.axsig.get_ylim()
        if self.PosAvailable:
            self.ZoomContext['posx'], self.ZoomContext['posX'] = self.axpos.get_xlim()
            self.ZoomContext['posy'], self.ZoomContext['posY'] = self.axpos.get_ylim()

    def restoreZoomContext(self, newVar):
        self.axsig.set_xlim(self.ZoomContext['1x'], self.ZoomContext['1X'])
        if newVar: 
            self.axsig.autoscale(axis='y')
        else: 
            self.axsig.set_ylim(self.ZoomContext['1y'], self.ZoomContext['1Y'])
        if self.PosAvailable:
            self.axpos.set_xlim(self.ZoomContext['posx'], self.ZoomContext['posX'])
            self.axpos.set_ylim(self.ZoomContext['posy'], self.ZoomContext['posY'])
#        self.draw()
        self.message = 'Ready'
        self.drawCursors()
        
    def clearZoomContext(self):
        self.axsig.autoscale()
        if self.PosAvailable: self.axpos.autoscale()
#        self.draw()
        self.message = 'Ready'
        self.drawCursors()
           
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
        
        if self.Sgn2Available and self.PlotMode == 0 : # signal 2 available and Traces display mode
            nval2 = self.Raw['Values2'][self.iNearest]
            self.message += '    ' + self.Var2_name + '=%.3f' %nval2
            
        if self.PosAvailable: # position map displayed
            self.HdlSelPos.set_xdata(nx)
            self.HdlSelPos.set_ydata(ny)
            self.message += '        Position : X=%.4f' %nx
            self.message += '    Y=%.4f' %ny
            
        if self.AbsAvailable: # abscissa signal available
            self.message += '    Absissa=%.4f' %nabs

        # second trace/statistic/spectrogram
        if (self.Sgn2Available and self.PlotMode == 0) or self.PlotMode == 1 or self.PlotMode == 2 :
            self.HdlSel2.set_xdata([nt, nt])
            self.HdlSel2.set_ydata([self.ax2.get_ylim()[0],self.ax2.get_ylim()[1]])
            
        if self.PlotMode == 1: # statistics displayed
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
