from PyQt4 import QtGui, QtCore

class AnalysisStackWidget(QtGui.QStackedWidget):

    """ Stack widget for listing 1D Analysis tool options.
    The order in make_options currently has to match the 
    order in internal_model of AnalysisSelectWidget.py
     
    Allows setting a size hint.    
        
    AnalysisSelectWidget(width, height)
    """

    def __init__(self, width, height):
        QtGui.QStackedWidget.__init__(self)
        self._width = width
        self._height = height
        self.make_options()
        self.set_defaultValues()

        # Lists for holding data temporarily
        self.eventData = []
        
    def sizeHint(self):
        return QtCore.QSize(self._width, self._height)

    def make_options(self):
        # Baseline 
        self.baselineTool = QtGui.QGroupBox('Options')
        self.baselineToolOptions = []
        self.baselineToolOptions.append(QtGui.QCheckBox('Keep original data', self.baselineTool))   
        make_groupBox_layout(self.baselineToolOptions, self.baselineTool)              
        self.addWidget(self.baselineTool)
        
        # Smooth 
        self.smoothTool = QtGui.QGroupBox('Options')
        self.smoothToolOptions = []
        self.smoothComboBox = QtGui.QComboBox()
        self.smoothComboBox.addItem('hanning')
        self.smoothComboBox.addItem('flat')
        self.smoothComboBox.addItem('hamming')
        self.smoothComboBox.addItem('bartlett')
        self.smoothComboBox.addItem('blackman')
        self.smoothToolOptions.append([self.smoothComboBox])
        self.smoothLength = QtGui.QLineEdit()
        self.smoothToolOptions.append([QtGui.QLabel('Window Length'), self.smoothLength])
        make_label_layout(self.smoothToolOptions, self.smoothTool)
        self.addWidget(self.smoothTool)             
        
        # Averaging 
        self.avgTool = QtGui.QGroupBox('Options')
        self.avgToolOptions = []
        self.avgToolOptions.append(QtGui.QCheckBox('Show traces', self.avgTool))
        self.avgToolOptions.append(QtGui.QCheckBox('Store result', self.avgTool))   
        make_groupBox_layout(self.avgToolOptions, self.avgTool)     
        self.addWidget(self.avgTool)
               
        # Measure 
        self.measureTool = QtGui.QGroupBox('Options')
        self.measureToolOptions = []
        self.measureToolOptions.append(QtGui.QCheckBox('Store result', self.measureTool))
        self.measureToolOptions.append(QtGui.QCheckBox('Minimum', self.measureTool))
        self.measureToolOptions.append(QtGui.QCheckBox('Maximum', self.measureTool))
        self.measureToolOptions.append(QtGui.QCheckBox('Mean', self.measureTool))      
        make_groupBox_layout(self.measureToolOptions, self.measureTool)
        self.addWidget(self.measureTool)
        
        # Event Detection 
        self.eventTool = QtGui.QGroupBox('Options')
        self.eventToolOptions = []
        self.eventDirection = QtGui.QComboBox()
        self.eventDirection.addItem('negative')
        self.eventDirection.addItem('positive')
        self.eventToolOptions.append([self.eventDirection])        
        self.eventThreshold = QtGui.QPushButton('Set Threshold', self)
        self.eventThreshold.setCheckable(True)
        self.eventThresholdDisplay = QtGui.QLabel('None')
        self.eventToolOptions.append([self.eventThreshold, self.eventThresholdDisplay])               
        self.eventNoiseSafety = QtGui.QLineEdit()
        self.eventToolOptions.append([QtGui.QLabel('Noise Safety'), self.eventNoiseSafety])
        self.eventSmooth = QtGui.QLineEdit()
        self.eventToolOptions.append([QtGui.QLabel('Smooth'), self.eventSmooth])
        self.eventCutOut = QtGui.QPushButton('Cut events', self)
        self.eventToolOptions.append([self.eventCutOut])
        self.eventBaseline = QtGui.QLineEdit()
        self.eventToolOptions.append([QtGui.QLabel('Baseline'), self.eventBaseline])
        self.eventDuration = QtGui.QLineEdit()
        self.eventToolOptions.append([QtGui.QLabel('Duration'), self.eventDuration])        
        make_label_layout(self.eventToolOptions, self.eventTool)
        self.addWidget(self.eventTool)        

    def add_options(self, optionList, groupBox):
        make_groupBox_layout(optionsList, groupBox)
        self.addWidget(groupBox)

    def set_defaultValues(self):
        # Event Detection
        self.eventNoiseSafety.setText('5')
        self.eventSmooth.setText('1')
        self.eventBaseline.setText('2')
        self.eventDuration.setText('20')


def make_groupBox_layout(optionsList, groupBox):
    """ Layout widgets vertically:
    
          |Option 1|
          |Option 2|
          |Option 3|
    """
    vbox = QtGui.QVBoxLayout()
    for widget in optionsList:
        vbox.addWidget(widget)
    vbox.addStretch(1)
    groupBox.setLayout(vbox)

def make_label_layout(optionsList, groupBox):
    """ Layout labels and widgets side by side, vertically
    using a grid layout:
    
         |Label 1    Option 1|
         |Label 2    Option 2|
         |Label 3    Option 3|                  
    """
    gridbox = QtGui.QGridLayout()
    row = 0
    for item in optionsList:
        if len(item)==1:
            gridbox.addWidget(item[0], row, 0)
        elif len(item)==2: 
            gridbox.addWidget(item[0], row, 0)
            gridbox.addWidget(item[1], row, 1)
        row+=1
    gridbox.setRowMinimumHeight(row,0)
    gridbox.setRowStretch(row,1)    
    groupBox.setLayout(gridbox)



