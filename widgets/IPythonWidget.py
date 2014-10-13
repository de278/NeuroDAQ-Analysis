import os
<<<<<<< HEAD
=======
from PyQt4 import QtGui, QtCore
>>>>>>> upstream/master

# Import the console machinery from ipython
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport
<<<<<<< HEAD
=======
#from IPython.core.shellapp import InteractiveShellApp

>>>>>>> upstream/master

class QIPythonWidget(RichIPythonWidget):
    """ Convenience class for a live IPython console widget. We can replace the standard banner using the customBanner argument"""
    def __init__(self,customBanner=None,*args,**kwargs):
        if customBanner!=None: self.banner=customBanner
<<<<<<< HEAD
        super(QIPythonWidget, self).__init__(*args,**kwargs)
=======
        super(QIPythonWidget, self).__init__(*args,**kwargs)        
        
        # Start in process kernel
>>>>>>> upstream/master
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt4'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

<<<<<<< HEAD
        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            guisupport.get_app_qt4().exit()            
=======
        # Pre import some modules and set some configuration options
        self.executeCommand('import numpy as np')
        self.executeCommand('import matplotlib.pylab as plt')
        self.executeCommand('%matplotlib inline')

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            #guisupport.get_app_qt4().exit()            
>>>>>>> upstream/master
        self.exit_requested.connect(stop)

    def pushVariables(self,variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)
    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()    
    def printText(self,text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)        
    def executeCommand(self,command):
        """ Execute a command in the frame of the console widget """
        self._execute(command,False)
<<<<<<< HEAD
=======
   

>>>>>>> upstream/master
