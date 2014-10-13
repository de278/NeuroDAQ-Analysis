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
        self.entryName = 'Measure'  
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
        self.toolOptions.append(QtGui.QCheckBox('Store result', self.toolGroupBox))
        self.toolOptions.append(QtGui.QCheckBox('Minimum', self.toolGroupBox))
        self.toolOptions.append(QtGui.QCheckBox('Maximum', self.toolGroupBox))
        self.toolOptions.append(QtGui.QCheckBox('Mean', self.toolGroupBox)) 
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Measure selected properties or statistics in the region defined
        by the data cursors.
    
        Options:
        1) create new entries in Working Data tree with the results
        """
    
        ############################################
        # ANALYSIS FUNCTION
       
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget
        data = aux.get_data(browser)  
        c1, c2 = aux.get_cursors(plotWidget) 
        dataIndex = plotWidget.plotDataIndex     
        saveData = False

        # Get dt list
        dtList = aux.get_attr(plotWidget.plotDataItems, 'dt')

        # Go through data and check selected values to measure
        # Can probably do this in a more efficient way
        results = []
        for option in self.toolOptions:
            if option.isChecked():
                if option.text()=='Store result':
                    saveData = True        

                if option.text()=='Minimum':
                    dataMin = []
                    for t in range(len(data)):
                        dt = dtList[t]
                        y = np.min(data[t][c1/dt:c2/dt])
                        x = np.argmin(data[t][c1/dt:c2/dt])
                        dataMin.append(y)
                        aux.plot_point(plotWidget, c1/dt, x, y, dt)
                    results.append(['Minimum', dataMin])        

                if option.text()=='Maximum':
                    dataMax = []
                    for t in range(len(data)):
                        dt = dtList[t]
                        y = np.max(data[t][c1/dt:c2/dt])
                        x = np.argmax(data[t][c1/dt:c2/dt])
                        dataMax.append(y)
                        aux.plot_point(plotWidget, c1/dt, x, y, dt)
                    results.append(['Maximum', dataMax])    

                if option.text()=='Mean':
                    dataMean = []
                    for t in range(len(data)):
                        dt = dtList[t]
                        y = np.mean(data[t][c1/dt:c2/dt])
                        dataMean.append(y)
                        plotWidget.plot([c1,c2], [y,y], pen=pg.mkPen('#CF1C04', width=1))
                    results.append(['Mean', dataMean])

        # Store results
        if saveData: aux.save_results(browser, 'Measurements', results)             
        ############################################  

