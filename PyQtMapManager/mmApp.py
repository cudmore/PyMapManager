"""
Main PyMapManager application interface using PyQt interface library.

Instantiate mmApplicationWindow to open the main window

Example::

    from PyQt4 import QtGui
    from pymapmanager.interface.mmApp import mmApplicationWindow

    qApp = QtGui.QApplication(sys.argv)
    aw = mmApplicationWindow()
    aw.show()
    sys.exit(qApp.exec_())

"""

import os
import sys # to make menus on osx, sys.platform == 'darwin'
import functools
from errno import ENOENT

from PyQt4 import QtGui, QtCore

from pymapmanager.mmMap import mmMap
from pymapmanager.interface.mmWindow import mmStackWindow, mmMapPlotWindow, mmStackPlotWindow
from pymapmanager.mmUtil import newplotdict

class mmApplicationWindow(QtGui.QMainWindow):
    """
    Main PyMapManager applicaiton window.
    This holds list widgets to display: maps, sessions, segments, and stats
    """

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.maps = []  # List of open pymapmanager.map
        self._windows = []  # list of open windows (use this to propogate selections)

        # set location of the window
        ag = QtGui.QDesktopWidget().availableGeometry()
        sg = QtGui.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = ag.width() - widget.width()
        y = 2 * ag.height() - sg.height() - widget.height()
        self.move(x, y)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        ##############################################################################
        # menus
        ##############################################################################
        """
        if sys.platform.startswith('darwin') :
            self.myMenuBar = QtGui.QMenuBar() # parentless menu bar for Mac OS
        else :
            self.myMenuBar = self.menuBar() # refer to the default one

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        #self.menuBar().addMenu(self.file_menu)
        self.myMenuBar.addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.myMenuBar.addSeparator()
        self.myMenuBar.addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)
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

        # can't add a quit menu, it is reserved on osx
        #self.file_menu.addSeparator()
        #self.file_menu.addAction('&Quit', self.fileQuit) #, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.view_menu = QtGui.QMenu('&View', self)
        self.view_menu.addAction('&Segments', self.about)
        self.view_menu.addAction('&Annotations', self.about)

        self.myMenuBar.addMenu(self.file_menu)
        self.myMenuBar.addMenu(self.view_menu)

        ##############################################################################
        # main widget
        ##############################################################################
        self.main_widget = QtGui.QWidget(self)

        mainToolbar = self.addToolBar('myToolbar')
        # loadMapAction = QtGui.QAction(QtGui.QIcon("open.bmp"), "Load", self)
        # loadMapAction = QtGui.QAction("Load", self)
        self.loadMapButton = QtGui.QPushButton("Load Map", self)
        #self.loadMapButton.clicked.connect(lambda: self.toolbarButton_callback(loadMapButton))
        self.loadMapButton.clicked.connect(functools.partial(self.toolbarButton_callback, 'loadMapButton'))

        self.loadMapDirButton = QtGui.QPushButton("Load Directory", self)
        #self.loadMapDirButton.clicked.connect(lambda: self.toolbarButton_callback(loadMapDirButton))
        self.loadMapDirButton.clicked.connect(functools.partial(self.toolbarButton_callback, 'loadMapDirButton'))

        self.defaultRoiType = QtGui.QComboBox(self)
        self.defaultRoiType.addItems(['spineROI', 'otherROI'])
        self.defaultRoiType.activated[str].connect(self.setDefaultRoiType)

        mainToolbar.addWidget(self.loadMapButton)
        mainToolbar.addWidget(self.loadMapDirButton)
        mainToolbar.addWidget(self.defaultRoiType)
        # mainToolbar.addAction(loadMapAction)
        # mainToolbar.actionTriggered[QtGui.QAction].connect(self.mainToolbar_callback)

        #
        gridLayout1 = QtGui.QGridLayout()

        # list of map
        mapLabel = QtGui.QLabel("Maps")
        self.mapListWidget = QtGui.QListWidget()
        self.mapListWidget.setMaximumWidth(150)
        self.mapListWidget.currentItemChanged.connect(self.map_list_changed)
        self.mapListWidget.doubleClicked.connect(self.plotmap0)

        # list of session
        sessLabel = QtGui.QLabel("Sessions")
        self.sessListWidget = QtGui.QListWidget()
        self.sessListWidget.setMaximumWidth(100)
        self.sessListWidget.currentItemChanged.connect(self.sess_list_changed)

        # list of segment
        segLabel = QtGui.QLabel("Segments")
        self.segListWidget = QtGui.QListWidget()
        self.segListWidget.setMaximumWidth(100)
        self.segListWidget.currentItemChanged.connect(self.seg_list_changed)

        gridLayout1.addWidget(mapLabel, 0, 0)
        gridLayout1.addWidget(self.mapListWidget, 1, 0)
        gridLayout1.addWidget(sessLabel, 0, 1)
        gridLayout1.addWidget(self.sessListWidget, 1, 1)
        gridLayout1.addWidget(segLabel, 0, 2)
        gridLayout1.addWidget(self.segListWidget, 1, 2)

        gridLayout1.setRowMinimumHeight(1, 200)

        #
        gridLayout2 = QtGui.QGridLayout()

        # list of y stat
        yStatLabel = QtGui.QLabel("Y Stat")
        self.ystatListWidget = QtGui.QListWidget()
        self.ystatListWidget.setMaximumWidth(200)
        for i in range(10):
            item = QtGui.QListWidgetItem("%i\tystat" % i)
            self.ystatListWidget.addItem(item)
        # self.segListWidget.currentItemChanged.connect(self.seg_list_changed)

        # list of x stat
        xStatLabel = QtGui.QLabel("X Stat")
        self.xstatListWidget = QtGui.QListWidget()
        self.xstatListWidget.setMaximumWidth(200)
        for i in range(10):
            item = QtGui.QListWidgetItem("%i\txstat" % i)
            self.xstatListWidget.addItem(item)
        # self.segListWidget.currentItemChanged.connect(self.seg_list_changed)

        gridLayout2.addWidget(yStatLabel, 0, 0)
        gridLayout2.addWidget(self.ystatListWidget, 1, 0)
        gridLayout2.addWidget(xStatLabel, 0, 1)
        gridLayout2.addWidget(self.xstatListWidget, 1, 1)

        gridLayout2.setRowMinimumHeight(1, 200)

        # main vertical layout
        l = QtGui.QVBoxLayout(self.main_widget)

        # sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        # dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)

        plotStackButton = QtGui.QPushButton("Plot Stack Stats")
        plotStackButton.clicked.connect(self.plotStackButton_callback)

        plotMapButton = QtGui.QPushButton("Plot Map Stats")
        plotMapButton.clicked.connect(self.plotMapButton_callback)

        plotStackImageButton = QtGui.QPushButton("Plot Stack Image")
        plotStackImageButton.clicked.connect(self.plotStackImageButton_callback)

        l.addLayout(gridLayout1)
        l.addLayout(gridLayout2)
        # l.addWidget(sc)
        # l.addWidget(dc)
        l.addWidget(plotStackButton)
        l.addWidget(plotMapButton)
        l.addWidget(plotStackImageButton)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

        # load a mm map
        if 0:
            defaultMap = '/Users/cudmore/Desktop/data/cudmore/rr30a/rr30a.txt'
            #defaultMap = '/Volumes/fourt/MapManager_Data/stroke1/stroke1.txt'
            if not os.path.isfile(defaultMap):
                raise IOError(ENOENT, 'mmApp did not find defaultMap:', defaultMap)
            print 'loading default map:', defaultMap
            self.loadMap(defaultMap)
            """
            defaultMap = '/Users/cudmore/Desktop/data/rr58c/rr58c.txt'
            if os.path.isfile(defaultMap):
                print 'loading default map:', defaultMap
                self.loadMap(defaultMap)
            else:
                print 'error loading map:', defaultMap
            """
        if 0:
            defaultMap = '/Users/cudmore/Dropbox/MapManagerData/server/public/amit1/amit1.txt'
            if not os.path.isfile(defaultMap):
                raise IOError(ENOENT, 'mmApp did not find defaultMap:', defaultMap)
            print 'loading default map:', defaultMap
            self.loadMap(defaultMap)
        # load from online repository
        if 1:
            urlmap = 'rr30a'
            self.loadMap(urlmap=urlmap)

        """
        #show a table widget
        tmp_df = self.maps[0].stacks[0].stackdb
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setRowCount(len(tmp_df.index))
        self.tableWidget.setColumnCount(len(tmp_df.columns))
        self.tableWidget.setHorizontalHeaderLabels(tmp_df.columns.values)
        for i in range(len(tmp_df.index)):
            for j in range(len(tmp_df.columns)):
                pass
                #used to work
                # #self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(str(tmp_df.iget_value(i, j))))
                # slow?
                # self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(str(tmp_df.iloc[i, j])))
        l.addWidget(self.tableWidget)
        """

        #
        # qtpandas
        '''
        from qtpandas.models.DataFrameModel import DataFrameModel
        from qtpandas.views.DataTableView import DataTableWidget
        model = DataFrameModel()
        widget = DataTableWidget()
        widget.resize(800, 600)
        widget.show()
        widget.setViewModel(model)
        model.setDataFrame(self.maps[0].stacks[0].stackdb)
        '''
        #
        #

        self.setAcceptDrops(True)

    def setDefaultRoiType(self, text):
        """Respond to roiType popup/QComboBox"""
        d = self.getState()
        if d['map']:
            d['map'].defaultRoiType = str(text)

    def broadcastevent(self, event):
        """Broadcast an event to all open application windows (self._windows) and call receiveevent(event)"""

        # if we don;t get a runMapRow but have a spine selection from a map then fill it in
        if event.type == 'spine selection':
            if not event.runMapRow >= 0:
                if event.map and event.mapSession>=0 and event.stackdbIdx>=0:
                    runMapIdx = 6
                    event.runMapRow = event.map.objMap[runMapIdx,event.stackdbIdx,event.mapSession]
                    event.runMapRow = int(event.runMapRow)

        for window in self._windows:
            window.receiveevent(event)

    def dragEnterEvent(self, event):
        """Changes the look of the main window when a file/folder is dragged over the window."""
        print event.mimeData()
        if event.mimeData().hasFormat("text/uri-list"):
            event.acceptProposedAction()
        event.acceptProposedAction()

    def dropEvent(self, event):
        """Handles opening a map, stack, or folder of maps/stacks when they are dropped on the main window."""
        urls = event.mimeData().urls()
        if urls:
            filename = urls[0].toLocalFile()
            if filename:
                print 'todo: implement drag and drop of folders, maps, and stacks, filename:', filename

    # def mainToolbar_callback(self, a):
    #    print 'mainToolbar_callback:', a

    def loadMap(self, path=None, urlmap=None):
        """Load a mmMap into application. Application keeps 'maps', a list of maps."""
        if urlmap is not None:
            serverurl = ''
            username = 'cudmore'

        elif path is None:
            # ask user for file
            path = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '/')
            path = str(path)
            if not path:
                return

        m = mmMap(filePath=path, urlmap=urlmap)
        self.maps.append(m)

        self.mapListWidget.clear()
        for i in range(len(self.maps)):
            item = QtGui.QListWidgetItem("%i\t%s" % (i, self.maps[i].name))
            self.mapListWidget.addItem(item)
        self.selectMap(0)

    def selectMap(self, idx):
        """Update the interface when user selects a different map or a new map is loaded"""
        self.statList = self.maps[idx].stacks[0].stackdb.columns.values

        # map
        self.mapListWidget.setCurrentRow(idx)
        # sess
        self.sessListWidget.clear()
        for i in range(self.maps[idx].numSessions):
            item = QtGui.QListWidgetItem("%i" % i)
            self.sessListWidget.addItem(item)
        self.sessListWidget.setCurrentRow(0)

        # seg
        self.segListWidget.clear()
        item = QtGui.QListWidgetItem('All')
        self.segListWidget.addItem(item)
        for i in range(self.maps[idx].numMapSegments):
            item = QtGui.QListWidgetItem("%i" % i)
            self.segListWidget.addItem(item)
        self.segListWidget.setCurrentRow(0)

        # ystat
        self.ystatListWidget.clear()
        self.xstatListWidget.clear()
        # todo: prepend map type (session, date, days, hours, minutes, zdays, zhours, zminutes)
        for i in range(len(self.statList)):
            statStr = self.statList[i]
            typeStr = 'stackdb'
            spaces = '   '
            if i < 10:
                spaces = '       '
            elif i < 100:
                spaces = '     '
            else:
                spaces = '   '
            spaces2 = '   '
            if statStr.endswith('_int1'):
                typeStr = 'int1'
                spaces2 = '          '
            elif statStr.endswith('_int2'):
                typeStr = 'int2'
                spaces2 = '          '
            item = QtGui.QListWidgetItem("%i%s%s%s%s" % (i, spaces, typeStr, spaces2, statStr))
            self.ystatListWidget.addItem(item)
            item = QtGui.QListWidgetItem("%i%s%s%s%s" % (i, spaces, typeStr, spaces2, statStr))
            self.xstatListWidget.addItem(item)
        self.ystatListWidget.setCurrentRow(3)
        self.xstatListWidget.setCurrentRow(2)

    def toolbarButton_callback(self, buttonID):
        print 'toolbarButton_callback:', buttonID
        if buttonID == 'loadMapButton':
            self.loadMap()

    def map_list_changed(self, curr, prev):
        # (curr,prev) are QListWidgetItem
        print 'ApplicationWindow.map_list_changed', curr
        print '   currentRow:', self.mapListWidget.currentRow()
        print '   ', self.mapListWidget.currentItem().text()

    def sess_list_changed(self, curr, prev):
        # (curr,prev) are QListWidgetItem
        print 'ApplicationWindow.sess_list_changed', curr
        print '   currentRow:', self.sessListWidget.currentRow()
        print '   ', self.sessListWidget.currentItem().text()

    def seg_list_changed(self, curr, prev):
        # (curr,prev) are QListWidgetItem
        print 'ApplicationWindow.seg_list_changed', curr
        print '   currentRow:', self.segListWidget.currentRow()
        print '   ', self.segListWidget.currentItem().text()

    def getState(self):
        """Capture the full state of the interface including selected: map, session, segment, ystat, xstat."""
        plotDict = newplotdict()

        # map
        mapIdx = self.mapListWidget.currentRow()
        plotDict['map'] = self.maps[mapIdx]
        plotDict['mapname'] = self.mapListWidget.currentItem().text()
        plotDict['mapidx'] = mapIdx # index into the list we are displaying

        # session
        sessIdx = self.sessListWidget.currentRow()
        plotDict['sessidx'] = sessIdx
        plotDict['stack'] = self.maps[mapIdx].stacks[sessIdx]

        # segment
        segStr = self.segListWidget.currentItem().text()
        if segStr == 'All':
            plotDict['segmentid'] = []
        else:
            plotDict['segmentid'] = [int(segStr)]

        # stat
        plotDict['ystat'] = self.statList[self.ystatListWidget.currentRow()]
        plotDict['xstat'] = self.statList[self.xstatListWidget.currentRow()]

        plotDict['roitype'] = ['spineROI']
        if plotDict['map'] is not None:
            plotDict['roitype'] = [plotDict['map'].defaultRoiType]

        return plotDict

    def closechildwindow(self, windowPtr):
        """called when we close a PlotWindow"""

        self._windows.remove(windowPtr)
        """
        for window in self._windows:
            if window == windowPtr:
                self._windows.remove(windowPtr)
        """

    def plotStackButton_callback(self):
        print 'ApplicationWindow.plotStackButton_callback()'

        # todo: add to list of open windows self._windows

        plotwindow = mmStackPlotWindow(self)
        self._windows.append(plotwindow)

        stateDict = self.getState()
        plotwindow.myCanvas.plot(stateDict)

        plotwindow.show()

    def plotMapButton_callback(self):
        print 'ApplicationWindow.plotMapButton_callback()'

        # todo: add to list of open windows self._windows

        plotwindow = mmMapPlotWindow(self)
        self._windows.append(plotwindow)

        stateDict = self.getState()
        #plotwindow.myCanvas.plot(stateDict)
        plotwindow.myCanvas.plot2(stateDict)

        plotwindow.show()

    def plotmap0(self):
        """Plot a session versus pDist map. This responds to double-click of a map in the map list."""

        # todo: add to list of open windows self._windows

        plotwindow = mmMapPlotWindow(self)
        self._windows.append(plotwindow)

        stateDict = self.getState()
        if stateDict['roitype'] == 'spineROI':
            stateDict['segmentid'] = [0]
            stateDict['ystat'] = 'pDist'
        elif stateDict['roitype'] == 'otherROI':
            stateDict['segmentid'] = []
            stateDict['ystat'] = 'runIdx'

        stateDict['xstat'] = 'mapSession'

        plotwindow.myCanvas.plotMap0(stateDict)

        plotwindow.show()

    def plotStackImageButton_callback(self):
        print 'ApplicationWindow.plotStackImageButton_callback()'

        # todo: add to list of open windows self._windows

        stateDict = self.getState()

        plotwindow = mmStackWindow(stateDict=stateDict, parent=self)
        self._windows.append(plotwindow)

        stateDict = self.getState()
        plotwindow.myCanvas.plot(stateDict)

        plotwindow.show()

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About", """Made by Robert H Cudmore.""")
