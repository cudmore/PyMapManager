"""
Tables to display stackdb pandas data frame
"""

from PyQt4 import QtGui, QtCore

class MyPandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, roiType='spineROI', parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

        self._roiType = [roiType]

    def rowCount(self, parent=None):
        #m = len(self._data['roiType'].isin(self._roiType).values)
        #return m
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None