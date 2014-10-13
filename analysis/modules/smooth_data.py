from PyQt4 import QtGui, QtCore

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
from analysis import smooth
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Smooth'  
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

    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.oneDimToolStackedWidget
        self.toolGroupBox = QtGui.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.comboBox = QtGui.QComboBox()
        self.comboBox.addItem('hanning')
        self.comboBox.addItem('flat')
        self.comboBox.addItem('hamming')
        self.comboBox.addItem('bartlett')
        self.comboBox.addItem('blackman')
        self.toolOptions.append([self.comboBox])
        self.smoothLength = QtGui.QLineEdit()
        self.toolOptions.append([QtGui.QLabel('Window Length'), self.smoothLength])        
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Smooth traces
    
        Options:
        1) Window type
        2) Window length
        """
    
        ############################################
        # ANALYSIS FUNCTION
        
        # Get options
        window = str(self.comboBox.currentText())
        window_len = float(self.smoothLength.text())
    
        # Get widgets
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget
    
        # Get parent text of plotted items
        try:
            parentText = plotWidget.plotDataItems[0].parent().text(0) # Assumes all plotted data have the same parent
        except AttributeError:   # Parent = None
            parentText = 'Data'
    
        # Smooth data
        results = [] 
        for item in plotWidget.plotDataItems:  
            # Copy attributes and add some new ones
            attrs = item.attrs
            attrs['smooth_window_type'] = window
            attrs['smooth_window_length'] = window_len
        
            # Smooth
            traceSmooth = smooth.smooth(item.data, window_len=window_len, window=window)
            results.append([item.text(0), traceSmooth, attrs])
        
            # Plot smoothed trace
            #x = np.arange(0, len(traceSmooth)*item.attrs['dt'], item.attrs['dt'])
            #plotWidget.plot(x, traceSmooth, pen=pg.mkPen('#F2EF44', width=1))
            
            smoothItem = aux.make_h5item('smooth', traceSmooth, item.attrs)
            pgplot.browse_singleData(browser, plotWidget, smoothItem, clear=False, color='#F2EF44')

        # Store results
        aux.save_results(browser, parentText+'_smooth', results)     
         
        ############################################  
      
      
