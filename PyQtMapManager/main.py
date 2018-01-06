
# todo: add tables to (stack,map) plot to show a small object database
# todo: finish callbacks for (stack, map, image) plot (1) pan, (2) zoom, (3) drag?, (4) select point
# todo: implement a 'segment plot' where we take average across a segment for one stat, e.g. bssSum
# todo: expand map list interface to include map condition
# todo: read session condition (from main map nv table) and start plotting x-axis as condition.
#           we will need to take average across spines (in obj map row) that have same condition
# todo: implement special x-axis for mapplot0 (session, date,days, zero days, etc)
#           add interface in main plot window to switch between these
# todo: add interface in main plot window to transform x/y as (%, abs, etc). This only make sense for mapplot0 where x-axis is (session, date, days, etc)

#from __future__ import unicode_literals
import sys, os, math

import numpy as np

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt4 import QtGui, QtCore

from pymapmanager.mmMap import mmMap
from pymapmanager.interface.mmApp import mmApplicationWindow

if __name__ == '__main__':

    if 1:
        qApp = QtGui.QApplication(sys.argv)

        aw = mmApplicationWindow()
        #aw.setWindowTitle("%s" % progname)
        aw.setWindowTitle('PyQtMapManager')
        aw.show()
        sys.exit(qApp.exec_())
        # qApp.exec_()

    if 0:
        from pymapmanager.mmStack import mmStack
        stack = mmStack(filePath='/Users/cudmore/Desktop/data/julia/01_HC_ch1.tif')
        stack.loadStackImages(channel=1)

    if 0:
        defaultMap = '/Users/cudmore/Desktop/data/rr30a/rr30a.txt'
        print 'loading map:', defaultMap
        m = mmMap(filePath=defaultMap)

        import pymapmanager
        pd = pymapmanager.mmUtil.newplotdict()

        ma = pymapmanager.mmMapAnalysis.mmMapAnalysis(m)
        ma.getDynamics(pd)

    if 0:
        from pymapmanager.mmStack import mmStackPool
        path = '/Users/cudmore/MapManagerData/richard/Nancy/rr30a/raw/'
        # path = '/Volumes/fourt/MapManagerData/richard/Nancy/'

        stacks = mmStackPool(path)
        print stacks

        for stack in stacks:
            print stack

        images = stacks.stacks[1].loadStackImages(channel=1)
        print images.shape

    if 0:
        import matplotlib.pyplot as plt

        from pymapmanager.mmMapPlot2 import mmMapPlot2
        from pymapmanager.mmUtil import newplotdict

        defaultMap = '/Users/cudmore/Desktop/data/rr30a/rr30a.txt'
        print 'loading map:', defaultMap
        m = mmMap(filePath=defaultMap)

        print m.stacks[0].stackdb

        plotDict = newplotdict()
        plotDict['segmentid'] = [0]

        mp = mmMapPlot2(m)
        fig = plt.figure()
        mp.plotMap0(fig, plotDict)