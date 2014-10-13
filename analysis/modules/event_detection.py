from PyQt4 import QtGui, QtCore

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
import scipy.signal as signal
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
from analysis import smooth
from widgets import h5Item
from util import pgplot
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Event Detection'  
        ############################################
        
        # Get main browser
        self.browser = browser          
        # Add entry to AnalysisSelectWidget         
        selectItem = QtGui.QStandardItem(self.entryName)
        selectWidget = self.browser.ui.oneDimToolSelect
        selectWidget.model.appendRow(selectItem)        
        # Add entry to tool selector        
        browser.customToolSelector.add_tool(self.entryName, self.func)
        # Add option widgets
        self.make_option_widgets()
        # Set default values
        self.set_defaultValues()

    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.oneDimToolStackedWidget
        self.toolGroupBox = QtGui.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.eventDirection = QtGui.QComboBox()
        self.eventDirection.addItem('negative')
        self.eventDirection.addItem('positive')
        self.toolOptions.append([self.eventDirection])
        self.eventThreshold = QtGui.QPushButton('Set Threshold')
        self.eventThreshold.setCheckable(True)
        self.eventThresholdDisplay = QtGui.QLabel('None')
        self.toolOptions.append([self.eventThreshold, self.eventThresholdDisplay])               
        self.eventNoiseSafety = QtGui.QLineEdit()
        self.toolOptions.append([QtGui.QLabel('Noise Safety'), self.eventNoiseSafety])
        self.eventSmooth = QtGui.QLineEdit()
        self.toolOptions.append([QtGui.QLabel('Smooth'), self.eventSmooth])
        self.eventCutOut = QtGui.QPushButton('Cut events')
        self.toolOptions.append([self.eventCutOut])
        self.eventBaseline = QtGui.QLineEdit()
        self.toolOptions.append([QtGui.QLabel('Baseline'), self.eventBaseline])
        self.eventDuration = QtGui.QLineEdit()
        self.toolOptions.append([QtGui.QLabel('Duration'), self.eventDuration])           
        
        # Connect buttons to functions
        self.eventCutOut.clicked.connect(self.event_cut)
        self.eventThreshold.toggled.connect(self.show_thresholdCursor)   
              
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)


    def func(self, browser):
        """ Temporary event detection function using amplitude
        threshold only. Noise safety is for when coming down from
        peak, go down an extra amount from threshold before starting
        to search for the next event.
        """
        ############################################
        # ANALYSIS FUNCTION
 
        # Read detection options 
        threshold = float(self.browser.ui.dataPlotsWidget.cursorThsPos)
        noiseSafety = float(self.eventNoiseSafety.text())
        smoothFactor = float(self.eventSmooth.text())
        direction = str(self.eventDirection.currentText())
        c1, c2 = aux.get_cursors(self.browser.ui.dataPlotsWidget) 

        # Ensure that noise safety has the same sign as the threshold
        noiseSafety = np.sign(threshold) * abs(noiseSafety)

        # Get dt list and attrs for use in concatenated data
        dtList = aux.get_attr(self.browser.ui.dataPlotsWidget.plotDataItems, 'dt')
        dt = dtList[0]
        item = self.browser.ui.dataPlotsWidget.plotDataItems[0]
        attrs = item.attrs

        # Get data currently plotted within the cursors and concatenate in a single sweep
        data = aux.get_data(self.browser)
        if browser.ui.dataPlotsWidget.cursor1Pos: data = data[:,c1/dt:c2/dt]
        data = data.ravel()

        # Smooth
        original_data = data
        if smoothFactor > 1:
            data = smooth.smooth(data, window_len=smoothFactor, window='hanning')

        # Run detection  
        if direction=='negative':
            comp = lambda a, b: a < b
        elif direction=='positive':
            comp = lambda a, b: a > b
        eventCounter,i = 0,0
        xOnsets, yOnsets = [], []
        while i<len(data):
            if comp(data[i],threshold):
                xOnsets.append(i)
                yOnsets.append(data[i])
                eventCounter +=1
                while i<len(data) and comp(data[i],(threshold-noiseSafety)):
                    i+=1 # skip values if index in bounds AND until the value is below/above threshold again
            else:
                i+=1

        frequency = eventCounter/(len(data)*dt)*1000   # in Hz
        print eventCounter, 'events detected at', frequency, 'Hz'

        # Store event onsets and peaks in h5 data tree
        results = []
        results.append(['trace', np.array(original_data), attrs])
        results.append(['onsets', np.array(xOnsets)])
        results.append(['peaks', np.array(yOnsets)])
        results.append(['number', np.array([eventCounter])])
        results.append(['frequency', np.array([frequency])])
        listIndexes = aux.save_results(browser, 'Event_Detection', results)    

        # Store list indexes temporarily in stack widget list for further event analysis
        self.eventItemsIndex = listIndexes

        # Plot results
        self.show_events(data, np.array(xOnsets), np.array(yOnsets), dt)
        ############################################            
        
        
    def event_cut(self):
        # Get trace and event onsets using stored dataIndex
        itrace = self.eventItemsIndex[0]
        trace = self.browser.ui.workingDataTree.dataItems[itrace]
        ionsets = self.eventItemsIndex[1]
        onsets = self.browser.ui.workingDataTree.dataItems[ionsets]   
        dt = float(trace.attrs['dt'])

        # Get cutting parameters
        baseline = float(self.eventBaseline.text())/dt
        duration = float(self.eventDuration.text())/dt 

        # Cut out
        events = []
        for onset in onsets.data:
            eStart = onset-baseline
            eEnd = onset+duration
            eData = trace.data[eStart:eEnd]
            events.append(eData)

        # Store event waveforms in h5 data tree
        results = []
        attrs = {}
        attrs['dt'] = dt 
        for e in np.arange(0, len(events)):
            results.append(['event'+str(e), events[e], attrs])  
        aux.save_results(self.browser, 'Events', results)
        

    def show_thresholdCursor(self):
        """ Show horizontal cursor to set threshold 
        """
        plotWidget = self.browser.ui.dataPlotsWidget
        if self.eventThreshold.isChecked():   
            plotWidget.cursorThsPos = 0
            plotWidget.cursorThs = pg.InfiniteLine(pos=plotWidget.cursorThsPos, angle=0, movable=True,
                                               pen=pg.mkPen('#FFD000', width=2))
            plotWidget.addItem(plotWidget.cursorThs)
            plotWidget.cursorThs.sigPositionChanged.connect(self.update_threshold)
        else:
            plotWidget.cursorThsPos = []
            plotWidget.removeItem(plotWidget.cursorThs)                    

        
    def update_threshold(self):
        plotWidget = self.browser.ui.dataPlotsWidget
        plotWidget.cursorThsPos = round(plotWidget.cursorThs.value(),2)
        self.eventThresholdDisplay.setText(str(plotWidget.cursorThsPos))

    def show_events(self, data, xOnsets, yOnsets, dt):
        plotWidget = self.browser.ui.dataPlotsWidget
        plotWidget.clear()
        x = np.arange(0, len(data)*dt, dt)
        plotWidget.plot(x, data)
        plotWidget.plot(xOnsets*dt, yOnsets, pen=None, symbol='o', symbolPen='r', symbolBrush=None, symbolSize=7)

    def set_defaultValues(self):
        self.eventNoiseSafety.setText('5')
        self.eventSmooth.setText('1')
        self.eventBaseline.setText('2')
        self.eventDuration.setText('20')


