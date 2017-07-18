
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

from mmMap import mmMap
from mmMapPool import mmMapPool
#from mmStackPlot import mmStackPlot
#from mmMapPlot import mmMapPlot

#progname = os.path.basename(sys.argv[0])
#progversion = "0.1"

from PyMapManager.interface.mmApp import mmApplicationWindow

if __name__ == '__main__':
    qApp = QtGui.QApplication(sys.argv)

    aw = mmApplicationWindow()
    #aw.setWindowTitle("%s" % progname)
    aw.setWindowTitle('PyQtMapManager')
    aw.show()
    sys.exit(qApp.exec_())
    # qApp.exec_()