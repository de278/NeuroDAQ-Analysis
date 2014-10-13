from PyQt4 import QtGui, QtCore

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Average'  
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
        self.toolOptions.append(QtGui.QCheckBox('Show traces', self.toolGroupBox))
        self.toolOptions.append(QtGui.QCheckBox('Store result', self.toolGroupBox))
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Calculate average trace from currently plotted traces.

        Options:
        1) create new entry in Working Data tree with the result
        2) plot average with orginal traces
        """
    
        ############################################
        # ANALYSIS FUNCTION
        
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget   

        # Clear plot and get data
        plotWidget.clear()    
        data = aux.get_data(browser)
    
        # Get dt and 
        dt = aux.get_attr(plotWidget.plotDataItems, 'dt')[0]

        # Calculate average
        avgData = np.mean(data,0)

        # Check selected options
        for option in self.toolOptions:
            if option.isChecked():
                if option.text()=='Store result':
                    results = []                                    
                    # Get attributes from plotted items
                    item = plotWidget.plotDataItems[0]
                    attrs = item.attrs           
 
                    # Store data     
                    results.append(['avg_trace', avgData, attrs])
                    aux.save_results(browser, item.parent().text(0)+'_average', results) 
             
                if option.text()=='Show traces':
                    pgplot.replot(browser, plotWidget)

        # Plot average
        item = aux.make_h5item('avg', avgData, plotWidget.plotDataItems[0].attrs)
        pgplot.browse_singleData(browser, plotWidget, item, clear=False, color='r')
        if browser.ui.actionShowCursors.isChecked(): pgplot.replot_cursors(browser, plotWidget)      
         
        ############################################  
        
        
        
        
        
