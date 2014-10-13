""" Functions for getting data in and out of .hdf5 files
and into H5 trees

Currently New File and Save As are saved to the folder currently
open in the file data tree.

Attributes are attached to datasets only, not to groups (yet).
"""

import sys, os, re, copy
import h5py
from PyQt4 import QtGui, QtCore
import sip
import numpy as np
from widgets import h5Item
import tablefuncs as table

def load_h5(browser, tree, push):
    browser.ui.fileDataTree.data = []
    index = browser.ui.dirTree.selectedIndexes()[0]
    currentFile = str(index.model().filePath(index))
    browser.currentFolder = os.path.dirname(currentFile)
    if browser.db: browser.db.close()
    if '.hdf5' in currentFile:
        #print self.currentFile
        browser.db = h5py.File(currentFile, 'r+')
        tree.clear()       
        # Insert groups into the tree and add data to internal data list
        for group in browser.db:
            item = h5Item([str(group)])
            item.path = '/'+str(group)
            tree.addTopLevelItem(item)
            populate_h5tree(browser, browser.db['/'+str(group)], parentWidget=item, push=push) 
        # Select first item of loaded list
        tree.setCurrentItem(tree.itemAt(0,0))

    if push:
        browser.ui.workingDataTree.setSortingEnabled(True)
        browser.ui.workingDataTree.propsDt = ''
        browser.ui.workingDataTree.propsDescription = ''
        for attr in browser.db.attrs:
            #print attr, browser.db.attrs[attr]
            if 'dt' in attr: browser.ui.workingDataTree.propsDt = str(browser.db.attrs[attr])
            if 'description' in attr:  browser.ui.workingDataTree.propsDescription = browser.db.attrs[attr]
        table.update_table(browser)
        browser.currentOpenFile = currentFile
        browser.currentSaveFile = currentFile
        browser.ui.workingDataTree.setHeaderLabels([os.path.split(currentFile)[1]])
        browser.ui.workingDataTree.setSortingEnabled(False)  # Otherwise it screws up drag and drop

def populate_h5tree(browser, parent, parentWidget, push):   
    if isinstance(parent, h5py.Group):
        for child in parent:
            #print parent[child]
            item = h5Item([child])
            item.path = re.findall('"([^"]*)"', str(parent))[0] + '/' + str(child)
            parentWidget.addChild(item)
            populate_h5tree(browser, parent[child], item, push)
    elif isinstance(parent, h5py.Dataset):
        set_attrs(parent, parentWidget)
        if push:
            try:
                parentWidget.data = parent[:]            
                parentWidget.listIndex = len(browser.ui.workingDataTree.dataItems)
                #browser.ui.workingDataTree.data.append(parent[:])            
                browser.ui.workingDataTree.dataItems.append(parentWidget)
            except ValueError:   # No data in the dataset
                sip.delete(parentWidget)


def populate_h5File(browser, parent, parentWidget):
    for i in range(parentWidget.childCount()):
        item = parentWidget.child(i)        
        if item.childCount()>0:
            parent.create_group(str(item.text(0)))
            populate_h5File(browser, parent[str(item.text(0))], parentWidget=item)
        else:
            #print 'creating dataset', str(item.text(0)), 'in', parent
            #dset = parent.create_dataset(str(item.text(0)), data=browser.ui.workingDataTree.data[item.dataIndex])
            dset = parent.create_dataset(str(item.text(0)), data=item.data)
            set_attrs(item, dset)

def populate_h5dragItems(browser, originalParentWidget, parentWidget):
    if originalParentWidget.childCount()>0:
        for c in range(originalParentWidget.childCount()):
            child = originalParentWidget.child(c)
            #itemName = make_nameUnique(parentWidget, child.text(0))
            i = h5Item([str(child.text(0))])
            i.path = child.path
            parentWidget.addChild(i)
            if child.childCount()>0:
                populate_h5dragItems(browser, child, i)
            else:
                set_attrs(child, i)
                i.listIndex = len(browser.ui.workingDataTree.dataItems)
                #browser.ui.workingDataTree.data.append(browser.db[child.path][:])
                i.data = browser.db[child.path][:]
                browser.ui.workingDataTree.dataItems.append(i)
    # For transferring datasets directly
    else:
        set_attrs(originalParentWidget, parentWidget)
        parentWidget.path = originalParentWidget.path
        parentWidget.listIndex = len(browser.ui.workingDataTree.dataItems)
        #browser.ui.workingDataTree.data.append(browser.db[originalParentWidget.path][:])
        parentWidget.data = browser.db[originalParentWidget.path][:]
        browser.ui.workingDataTree.dataItems.append(parentWidget)

def create_h5(browser, tree):
    fname, ok = QtGui.QInputDialog.getText(browser, 'New file', 'Enter file name:')
    if ok: 
        browser.ui.workingDataTree.data = []
        tree.clear()
        browser.ui.workingDataTree.saveStr = fname     
        browser.ui.workingDataTree.propsDt = ''
        browser.ui.workingDataTree.propsDescription = ''   
        table.update_table(browser)
        browser.ui.workingDataTree.setHeaderLabels([fname])
        browser.currentSaveFile = browser.currentFolder + '/' + fname + '.hdf5'           


def save_h5(browser, tree):
    currentSaveFile = str(browser.currentSaveFile)
    browser.ui.workingDataTree.setHeaderLabels([os.path.split(currentSaveFile)[1]])
    if browser.db:
        browser.db.close()
        browser.db = None
    browser.wdb = h5py.File(currentSaveFile, 'w')
    root = tree.invisibleRootItem()
    populate_h5File(browser, browser.wdb['/'], root) 
    # File attributes    
    browser.wdb.attrs['dt'] =  str(browser.ui.workingDataTree.propsDt) 
    browser.wdb.attrs['description'] =  str(browser.ui.workingDataTree.propsDescription)     
    browser.wdb.close()

def set_attrs(source, item):
    """ Set attributes of h5 item or dataset
    Source and item can be tree h5item or h5File dataset, the syntax is the same.
    """
    for attr in source.attrs:
        item.attrs[attr] = source.attrs[attr] 

def make_nameUnique(browser, parentWidget, name):
    """ Check existing names in parentWidget that start with 'name'
    and get the next available index, as 'name_index'.
    Returns 'name' if unique, or 'name_index'
    """
    name = str(name)
    if not parentWidget:
        parentWidget = browser.ui.workingDataTree.invisibleRootItem()
    if parentWidget.childCount()>0:
        #print 'there are', parentWidget.childCount(), 'children'
        existingNames = []
        for c in range(parentWidget.childCount()):
            child = parentWidget.child(c)
            s = str(child.text(0)).strip(name+'_')
            if not s:  # Name is the same, the strip operation gives ''
                existingNames.append(0)
            else:
                existingNames.append(int(s))
        if np.max(existingNames)>0:
            name = name + '_' + str(np.max(existingNames)+1)
    print existingNames
    print 'name is', name
    return name
        
