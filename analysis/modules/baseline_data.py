from PyQt4 import QtGui, QtCore

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Baseline'  
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
        self.toolOptions.append(QtGui.QCheckBox('Keep original data', self.toolGroupBox))
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Subtract a baseline from the currently plotted traces.
        Baseline is the average of all datapoints between the 
        current position of the data cursors. 
    
        Options:
        1) keep original traces intact and create processed copies
        """
    
        ############################################
        # ANALYSIS FUNCTION
        
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget   
        c1, c2 = aux.get_cursors(plotWidget) 

        # Check selected options
        for option in self.toolOptions:
            if option.isChecked():
                if option.text()=='Keep original data':
                    aux.make_data_copy(browser, plotWidget)

        # Get the data now, in case we are working on a copy
        plotWidget.clear()    
        data = aux.get_data(browser)
    
        # Get dt
        dt = aux.get_attr(plotWidget.plotDataItems, 'dt')[0]

        # Make average between cursors and subract for each trace 
        for item in plotWidget.plotDataItems:
            bsl = np.mean(item.data[c1/dt:c2/dt])
            item.data = item.data - bsl

        # Re-plot data
        pgplot.replot(browser, plotWidget)
        pgplot.replot_cursors(browser, plotWidget)       
         
        ############################################            
        
        
