"""This module defines MapManager window classes.

    :class:`pymapmanager.interface.mmWindow`:
    Base class for other windows to inherit from

    :class:`pymapmanager.interface.mmStackWindow`:
    Display and interact with the 3D image and annotations from a :class:`pymapmanager.mmStack`.

    :class:`pymapmanager.interface.mmStackPlotWindow`:
    Display and interact with a plot of a annotations from a:class:`pymapmanager.mmStack`.

    :class:`pymapmanager.interface.mmMapPlotWindow`:
    Display and interact with a plot of :class:`pymapmanager.mmStack`
    annotations accross a :class:`pymapmanager.mmMap`.

"""

import sys, math

from PyQt4 import QtGui, QtCore

#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from pymapmanager.interface.mmCanvas import mmStackCanvas, mmMapPlotCanvas, mmStackPlotCanvas
from pymapmanager.interface.mmTable import MyPandasModel

class mmWindow(QtGui.QMainWindow):
    """
    A second QMainWindow to hold a plot. Possible plots are: stack image, stack, and map. StackImageWindow derives from this to plot a stack image.
    """
    def __init__(self, parent=None):
        super(mmWindow, self).__init__(parent)

        self.parent = parent

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("mm plot window")

        self.window_menu = QtGui.QMenu('&Window', self)
        self.window_menu.addAction('&Close', self.close,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_W)
        self.menuBar().addMenu(self.window_menu)

        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('...')

        self.resize(500, 500)

        self.main_widget = QtGui.QWidget(self)

        #toolbar
        self.toolbar = self.addToolBar('myToolbar')

        #graphs
        self.mainLayout = QtGui.QVBoxLayout(self.main_widget)

        # make sure these are done in derived classes
        #self.myCanvas = MyMplCanvas(parent=self, width=400, height=300, dpi=100)
        #self.navBar = NavigationToolbar(self.myCanvas, self)

        #self.mainLayout.addWidget(self.myCanvas)
        #self.mainLayout.addWidget(self.navBar)

        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        #self.statusBar().showMessage("This is main MapManager plot window", 2000)

    def closeEvent(self, event):
        """On close, remove self from xxx list"""
        print 'PlotWindow.closeEvent()'
        self.parent.closechildwindow(self)

    def setStatus(self, str):
        self.statusBar.showMessage(str)

    def broadcastevent(self, event):
        """Broadcast an event to all open application windows (self._windows) and call receiveevent(event).
        The main application is the only one who can broadcast.

        event : A mmEvent object with params to describe the event
        """
        self.parent.broadcastevent(event)

    def receiveevent(self, event):
        print 'PlotWindow.receiveevent()', event.type
        self.myCanvas.receiveevent(event)


class mmStackWindow(mmWindow):
    """Hold a stack image plot."""
    def __init__(self, stateDict=None, parent=None):
        mmWindow.__init__(self, parent=parent)

        self.stateDict = stateDict
        self.myCanvas = None

        sliderMax = math.pow(2,16) - 1
        self.lowContrast = 0
        self.highContrast = sliderMax

        # min contrast
        self.lowContrastLayout = QtGui.QHBoxLayout(self.main_widget)

        self.lowContrastLabel = QtGui.QLabel('Low')

        self.lowContrastSpinner = QtGui.QSpinBox()
        self.lowContrastSpinner.valueChanged.connect(self._valuechange_spinner)
        self.lowContrastSpinner.setMinimum(0)
        self.lowContrastSpinner.setMaximum(sliderMax)
        self.lowContrastSpinner.setValue(0)

        self.lowContrastSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.lowContrastSlider.valueChanged.connect(self._valuechange_slider)
        self.lowContrastSlider.setMinimum(0)
        self.lowContrastSlider.setMaximum(sliderMax)
        self.lowContrastSlider.setValue(0)
        #self.sl.setTickPosition(QSlider.TicksBelow)

        self.lowContrastLayout.addWidget(self.lowContrastLabel)
        self.lowContrastLayout.addWidget(self.lowContrastSpinner)
        self.lowContrastLayout.addWidget(self.lowContrastSlider)

        # max contrast
        self.highContrastLayout = QtGui.QHBoxLayout(self.main_widget)

        self.highContrastLabel = QtGui.QLabel("High")

        self.highContrastSpinner = QtGui.QSpinBox()
        self.highContrastSpinner.valueChanged.connect(self._valuechange_spinner)
        self.highContrastSpinner.setMinimum(0)
        self.highContrastSpinner.setMaximum(sliderMax)
        self.highContrastSpinner.setValue(sliderMax)

        self.highContrastSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.highContrastSlider.valueChanged.connect(self._valuechange_slider)
        self.highContrastSlider.setMinimum(0)
        self.highContrastSlider.setMaximum(sliderMax)
        self.highContrastSlider.setValue(sliderMax)

        self.highContrastLayout.addWidget(self.highContrastLabel)
        self.highContrastLayout.addWidget(self.highContrastSpinner)
        self.highContrastLayout.addWidget(self.highContrastSlider)

        ##############################################################################
        # docable widget to show stackdb as a table
        ##############################################################################

        # see here for excellent code on switching this from widget to view to use DOM
        # https://stackoverflow.com/questions/7782015/how-can-i-select-by-rows-instead-of-individual-cells-in-qtableview-in-pyqt

        #
        # segment list
        self.mySegmentDoc = QtGui.QDockWidget("Segments", self)

        numCol = 2
        numRow = 5
        colLabels = ['Segment', 'um']
        self.segmentTable = QtGui.QTableWidget(self)
        self.segmentTable.setRowCount(numRow)
        self.segmentTable.setColumnCount(numCol)
        self.segmentTable.setHorizontalHeaderLabels(colLabels)
        #self.tableWidget.setFixedWidth(100)
        #self.segmentTable.horizontalHeader().setStretchLastSection(True)
        for i in range(numRow):
            for j in range(numCol):
                self.segmentTable.setItem(i, j, QtGui.QTableWidgetItem(str(i*j + j)))
                #pass
                #used to work
                #self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(str(tmp_df.iget_value(i, j))))
                # slow?
                # self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(str(tmp_df.iloc[i, j])))
        self.segmentTable.setSelectionBehavior(QtGui.QTableWidget.SelectRows)
        #self.segmentTable.resizeColumnsToContents()

        self.mySegmentDoc.setWidget(self.segmentTable)
        self.mySegmentDoc.setFloating(False)
        #self.mySegmentDoc.resize(self.segmentTable.size())
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.mySegmentDoc)

        #  not sure how to do this, i want the doc to size to the size of the enclosed widget?


        #
        # stack db dock
        self.myStackdbDoc = QtGui.QDockWidget("Annotations", self)

        numCol = 4
        numRow = 100
        colLabels = ['roiType', 'x', 'y', 'z']

        roiType = self.stateDict['roitype']

        stackdb_df = self.stateDict['map'].stacks[0].stackdb
        stackdb_df['Idx'] = stackdb_df.index # Idx gets eaten when used as index, add a new column named 'Idx'
        stackdb_df = stackdb_df[stackdb_df['roiType'].isin(roiType)]
        stackdb_df = stackdb_df[['Idx', 'parentID', 'z']]
        myModel = MyPandasModel(stackdb_df)

        self.stackdbTable = QtGui.QTableView(self)

        self.stackdbTable.setModel(myModel)

        '''
        self.stackdbTable.setRowCount(numRow)
        self.stackdbTable.setColumnCount(numCol)
        self.stackdbTable.setHorizontalHeaderLabels(colLabels)
        
        #self.stackdbTable.setStyleSheet("gridline-color: rgb(191, 0, 0)") # sets the grid
        #self.tableWidget.setFixedWidth(100)
        #self.stackdbTable.horizontalHeader().setStretchLastSection(True)
        evenRow = True
        for i in range(numRow):
            for j in range(numCol):
                tableItem = QtGui.QTableWidgetItem(str(i*j + j))
                if evenRow:
                    tableItem.setBackground(QtGui.QColor(200,200,200))
                else:
                    tableItem.setBackground(QtGui.QColor('White'))
                self.stackdbTable.setItem(i, j, tableItem)
                #pass
                #used to work
                #self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(str(tmp_df.iget_value(i, j))))
                # slow?
                # self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(str(tmp_df.iloc[i, j])))
            evenRow = not evenRow
        self.stackdbTable.resizeColumnsToContents()
        '''
        self.stackdbTable.setSelectionBehavior(QtGui.QTableWidget.SelectRows)
        self.stackdbTable.setAlternatingRowColors(True)

        self.myStackdbDoc.setWidget(self.stackdbTable)
        self.myStackdbDoc.setFloating(False)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.myStackdbDoc)

        ##############################################################################
        # menus
        ##############################################################################
        """
        if sys.platform.startswith('darwin') :
            self.myMenuBar = QtGui.QMenuBar()
        else:
            self.myMenuBar = self.menuBar() # refer to the default one
        #self.myMenuBar.setNativeMenuBar(True)
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Load Map', self.about)
        self.file_menu.addSeparator()
        self.file_menu.addAction('&Close Map', self.about)
        """

        self.view_menu = QtGui.QMenu('&View', self)
        self.view_menu.addAction(self.mySegmentDoc.toggleViewAction())
        self.view_menu.addAction(self.myStackdbDoc.toggleViewAction())

        #self.myMenuBar.addMenu(self.file_menu)
        #self.myMenuBar.addMenu(self.view_menu)
        self.menuBar().addMenu(self.view_menu)

        ##############################################################################
        #  IMPORTANT
        #  main canvas to draw images and overlay points
        ##############################################################################
        self.myCanvas = mmStackCanvas(parent=self) # main widget, IMPORTANT
        #self.navBar = NavigationToolbar(self.myCanvas, self)

        self.mainLayout.addLayout(self.lowContrastLayout)
        self.mainLayout.addLayout(self.highContrastLayout)
        self.mainLayout.addWidget(self.myCanvas)
        #self.mainLayout.addWidget(self.navBar)

    def _valuechange_slider(self):
        self.lowContrast = self.lowContrastSlider.value()
        self.highContrast = self.highContrastSlider.value()
        # update spinner
        self.lowContrastSpinner.setValue(self.lowContrast)
        self.highContrastSpinner.setValue(self.highContrast)

        if self.myCanvas:
            self.myCanvas.setSliceContrast()
            self.myCanvas.draw()

    def _valuechange_spinner(self):
        self.lowContrast = self.lowContrastSpinner.value()
        self.highContrast = self.highContrastSpinner.value()
        # update slider
        self.lowContrastSlider.setValue(self.lowContrast)
        self.highContrastSlider.setValue(self.highContrast)

        if self.myCanvas:
            self.myCanvas.setSliceContrast()
            self.myCanvas.draw()

class mmMapPlotWindow(mmWindow):
    """Display a map plot of points.

    Todo: instantiate this with a stateStruct so we can figure out number of session for session spinner interface
    """
    def __init__(self, parent=None):
        mmWindow.__init__(self, parent=parent)

        tmpMaxSession = 20

        # spinner to select session
        self.sessionLayout = QtGui.QHBoxLayout(self.main_widget)

        self.sessionSpinnerLabel = QtGui.QLabel("Session")

        self.sessionSpinner = QtGui.QSpinBox()
        self.sessionSpinner.valueChanged.connect(self._valuechange_spinner)
        self.sessionSpinner.setMinimum(0)
        self.sessionSpinner.setMaximum(tmpMaxSession)
        self.sessionSpinner.setValue(0)

        self.sessionLayout.addWidget(self.sessionSpinnerLabel)
        self.sessionLayout.addWidget(self.sessionSpinner)

        # the canvas that holds plot, does all drawing and responds to user (IMPORTANT)
        self.myCanvas = mmMapPlotCanvas(parent=self) # main canvas to display and interact with plot (IMPORTANT)

        # matplotlib toolbar
        #self.navBar = NavigationToolbar(self.myCanvas, self)

        self.mainLayout.addLayout(self.sessionLayout)
        self.mainLayout.addWidget(self.myCanvas)
        #self.mainLayout.addWidget(self.navBar)

    def _valuechange_spinner(self):
        val = self.sessionSpinner.value()
        d = self.myCanvas.myPlotDict
        d['segmentID'] = [val]
        self.myCanvas.plotMap0(d)

class mmStackPlotWindow(mmWindow):
    """Display a stack plot of points."""
    def __init__(self, parent=None):
        mmWindow.__init__(self, parent=parent)

        self.myCanvas = mmStackPlotCanvas(parent=self)
        #self.navBar = NavigationToolbar(self.myCanvas, self)

        self.mainLayout.addWidget(self.myCanvas)
        #self.mainLayout.addWidget(self.navBar)


