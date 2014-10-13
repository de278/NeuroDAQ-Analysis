from PyQt4 import QtGui, QtCore

class AnalysisSelectWidget(QtGui.QListView):

    """ Reimplement QListView Class for displaying a list of tools
    
    Allows setting a size hint.    
    AnalysisSelectWidget(width, height)
    """

    def __init__(self, width, height):
        QtGui.QListView.__init__(self)
        self._width = width
        self._height = height
        self.internal_model()
        
    def sizeHint(self):
        return QtCore.QSize(self._width, self._height)
        
    def internal_model(self):
        self.model = QtGui.QStandardItemModel(self)
        tools = [
            'Baseline',
            'Smooth',
            'Average',
            'Measure',
            'Event Detection',
            'Custom' 
        ]
        for tool in tools:
            item = QtGui.QStandardItem(tool)
            self.model.appendRow(item)
        self.setModel(self.model)
