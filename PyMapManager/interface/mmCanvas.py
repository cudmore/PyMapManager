"""
This module implements canvas classes to do the drawing inside PyMapManager windows

    StackImageCanvase: Canvas to display and interact with an 3D image volume (stack)

    mapplotcanvas:
    stackplotcanvas:
    segmentplotcanvas:
"""

import math
import numpy as np

from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from pymapmanager.mmUtil import mmEvent, newplotdict
from pymapmanager.mmMapPlot2 import mmMapPlot2

class mmCanvas(FigureCanvas):
    """A figure canvas that holds a matplotlib figure. User actions are linked to this canvas with mpl_connect. This canvas must have Qt.ClickFocus to receive user events."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.parent = parent

        self.stateDict = None
        self.plotPointObj = None # used to select points(s) in derived mmStackPlot and mmStackImage
        self.myWinType = None
        self.plotRunObj = None

        self.dynamics_on = False
        self.lines_on = False

        self.figure = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = self.figure.add_subplot(111)
        self.axes = self.figure.add_axes([0, 0, 1, 1]) #remove white border
        self.axes.axis('off') #turn off axis labels

        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.mpl_connect('key_press_event', self.onkey)
        self.mpl_connect('button_press_event', self.onclick)
        self.mpl_connect('scroll_event', self.onscroll)
        self.mpl_connect('pick_event', self.onpick)

        # self.canvas.setFocusPolicy( Qt.ClickFocus )
        # self.canvas.setFocus()
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setFocus()
        self.myScatterPlot = None
        self.myLinePlot = None

    def plot(self, stateDict):
        """All derived classes should over-ride this and have code to plot.

        stateDict: Dictionary describing what to plot. See mmApplication.getState()
        """
        pass

    def onkey(self, event):
        print 'mmCanvas.onkey()', event.key
        key = event.key

        #
        #  pan the plot
        xLim = self.axes.get_xlim()
        yLim = self.axes.get_ylim()
        xPercent = abs(xLim[1] - xLim[0]) * 0.1
        yPercent = abs(yLim[1] - yLim[0]) * 0.1
        if key == 'right':
            xLim += xPercent
            self.axes.set_xlim(xLim)
            self.draw()
        elif key == 'left':
            xLim -= xPercent
            self.axes.set_xlim(xLim)
            self.draw()
        elif key == 'up':
            yLim += yPercent
            self.axes.set_ylim(yLim)
            self.draw()
        elif key == 'down':
            yLim -= yPercent
            self.axes.set_ylim(yLim)
            self.draw()

        #
        # dynamics
        elif key == 'd':
            self.toggledynamics()
            self.draw()

        elif key == 't':
            if self.myScatterPlot:
                self.myScatterPlot.set_visible(not self.myScatterPlot.get_visible())
            if self.myLinePlot:
                self.myLinePlot.set_visible(not self.myLinePlot.get_visible())
            self.draw()

        elif key == 'esc':
            print 'esc needs to cancel spine selection'

    def togglelines(self, onoff=None):
        """Toggle lines connecting annotations between timepoint. Be carefull here on repeatedly plot these lines"""

    def toggledynamics(self, onoff=None):
        """Turn dynamics marker color on and off"""

    def onclick(self, event):
        print 'mmCanvas.onclick()', event.button, event.x, event.y, event.xdata, event.ydata

    def onscroll(self, event):
        print 'mmCanvas.onscroll()'

    def receiveevent(self, event):
        print 'mmCanvas.receiveevent()', event.type

    def onpick(self, event):
        """
        Respond to clicks in a map, stack, and image plot.
        """
        print 'mmCanvas.onpick()', event.ind

class mmMapPlotCanvas(mmCanvas):
    """Plot and interact with a plot of stack values across a map"""

    def __init__(self, parent=None):
        mmCanvas.__init__(self, parent=parent)

    def togglelines(self, onoff=None):
        """Toggle lines connecting annotations between timepoint. Be carefull here on repeatedly plot these lines"""

        if onoff:
            self.lines_on = onoff
        else:
            self.lines_on = ~self.lines_on

        if self.lines_on:
            linewidth = 0.5
            self.myLinePlot = self.axes.plot(self.xPlot.transpose(), self.yPlot.transpose(), c='k',
                                              linewidth=linewidth,
                                              zorder=-1)
        else:
            for i, line in enumerate(self.axes.lines):
                ax.lines.pop(i)
                line.remove()

    def toggledynamics(self, onoff=None):
        """Turn dynamics marker color on and off"""

        if onoff:
            self.dynamics_on = onoff
        else:
            self.dynamics_on = not self.dynamics_on

        if self.dynamics_on:
            # color add/sub/transient/persistent
            alpha = 1
            cNone = (0, 0, 0, alpha)
            cSubtract = (1, 0, 0, alpha)
            cAdd = (0, 1, 0, alpha)
            cTransient = (0, 0, 1, alpha)
            cPersistent = (1, 1, 0, alpha)

            cMatrix = []

            m = self.yRunRow.shape[0]
            n = self.yRunRow.shape[1]

            for i in range(m):
                for j in range(n):
                    currColor = cNone
                    prev = 'nan'
                    next = 'nan'
                    if j > 0:
                        prev = self.sessIdx[i][j - 1] >= 0
                    if j < n - 1:
                        next = self.sessIdx[i][j + 1] >= 0
                    if not prev and j > 0:
                        currColor = cAdd
                    if not next and j < n - 1:
                        currColor = cSubtract
                    if not prev and not next and j > 0 and j < n - 1:
                        currColor = cTransient
                    if prev and next:
                        currColor = cPersistent

                    cMatrix.append(currColor)
        else:
            cMatrix = 'b'

        self.myScatterPlot.set_color(cMatrix)

    def receiveevent(self, event):
        print 'mmMapPlotCanvas.receiveevent()', event.type
        if event.map != self.map:
            return
        if event.type == 'spine selection':
            # for a map, we should select a run
            if self.myWinType == 'map_plot':
                #xRun = self.xPlot[event.runMapRow, :]
                #yRun = self.yPlot[event.runMapRow, :]
                xRun = self.myMapPlot.x[event.runMapRow, :]
                yRun = self.myMapPlot.y[event.runMapRow, :]
                if self.plotRunObj:
                    self.plotRunObj.set_xdata(xRun)
                    self.plotRunObj.set_ydata(yRun)
                else:
                    # this is assuming we only plotted one line
                    self.plotRunObj = self.axes.plot(xRun, yRun, 'yo-')[0]
                self.draw()

    def onkey(self, event):
        print 'MyStaticMplCanvas.onkey()', event.key
        super(mmMapPlotCanvas, self).onkey(event)

    def onpick(self, event):
        """
        Respond to clicks in a map plot.

        event.ind: A list of hit points, just use the first.
        We are normally plotting self.runMap (a 2D nparray) with NaN.
        event.ind is index into this array AFTER nan has been stripped.
        """

        print 'mmMapPlotCanvas.onpick()', event.ind
        ind = event.ind
        if not len(ind) >= 1:
            return

        # strip nan, use this to find
        #yRunRow_noNan = self.yRunRow[~np.isnan(self.yRunRow)]
        #runMapRow = int(yRunRow_noNan[ind[0]])

        sessIdx, stackdbIdx = self.myMapPlot.getUserSelection(ind[0])
        print 'sessIdx:', sessIdx, 'stackdbIdx:', stackdbIdx

        """
        sessIdx_noNan = self.sessIdx[~np.isnan(self.sessIdx)]
        sessIdx = int(sessIdx_noNan[ind[0]])

        stackdbIdx_noNan = self.stackdbIdx[~np.isnan(self.stackdbIdx)]
        stackdbIdx = int(stackdbIdx_noNan[ind[0]])

        # transmit selection event to all open windows
        newEvent = mmEvent(self.map, sessIdx, stackdbIdx)
        """
        newEvent = mmEvent(self.map, sessIdx, stackdbIdx)
        self.parent.broadcastevent(newEvent)

        statusStr = newEvent.getText()
        self.parent.setStatus(statusStr)

    def plot2(self, stateDict):
        """
        Trying to get mmMapPlot working
        """
        self.myPlotDict = stateDict

        self.myWinType = 'map_plot'
        self.map = stateDict['map']

        self.myMapPlot = mmMapPlot2(stateDict['map'])
        self.myMapPlot.plotMap(self.figure, stateDict)

    def plot(self, stateDict):
        """Plot mmStack values for all mmStack(s) in the map."""

        self.myPlotDict = stateDict

        self.myWinType = 'map_plot'
        self.map = stateDict['map']

        stateDict = self.map.getMapValues3(stateDict)

        self.xPlot = stateDict['x']
        self.yPlot = stateDict['y']
        self.stackdbIdx = stateDict['stackidx']
        self.sessIdx = stateDict['mapsess']
        self.yRunRow = stateDict['runrow']

        self.myScatterPlot = self.axes.scatter(self.xPlot, self.yPlot, marker='o', picker=True)

        self.axes.set_xlabel(stateDict['xstat'])
        self.axes.set_ylabel(stateDict['ystat'])

    def plotMap0(self, stateDict):
        """
        Plot a canonical map of pDist versus session.

        stateDict: Tells us map to plot
        """

        self.myPlotDict = stateDict

        ## this should be in a common function mapPlot
        self.myWinType = 'map_plot'

        # this is silly, we should be given a map on construction?
        self.map = stateDict['map']

        self.myMapPlot = mmMapPlot2(stateDict['map'])
        self.myMapPlot.plotMap(self.figure, stateDict)

        """
        stateDict = self.map.getMapValues3(stateDict)

        self.xPlot = stateDict['x']
        self.yPlot = stateDict['y']

        # get spine angle and offset
        offset = 0.1
        cAngle = self.map.getMapValues2('cAngle', segmentID=stateDict['segmentid'])
        self.xPlot[cAngle > 180] += offset
        self.xPlot[cAngle < 180] -= offset

        markersize = 10  # units here is area
        self.myScatterPlot = self.axes.scatter(self.xPlot, self.yPlot, marker='o', s=markersize, picker=True)

        self.toggledynamics(True)
        self.togglelines(True)

        # background colors
        grayLevel = 0.6
        backgroundColor = (grayLevel, grayLevel, grayLevel)
        rect = self.figure.patch
        rect.set_facecolor(backgroundColor)  # figure background color
        # this works for matplotlib 2.02 but not earlier as is on my laptop
        # #self.axes.set_facecolor(backgroundColor) #axes background color

        # remove frame
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        self.axes.set_xlabel(stateDict['xstat'])
        self.axes.set_ylabel(stateDict['ystat'])
        """

class mmStackPlotCanvas(mmCanvas):
    """Plot and interact with a plot of stack values across a map"""

    def __init__(self, parent=None):
        mmCanvas.__init__(self, parent=parent)

    def toggledynamics(self, onoff=None):
        """Turn dynamics marker color on and off"""

        if onoff:
            self.dynamics_on = onoff
        else:
            self.dynamics_on = not self.dynamics_on

        """
        if self.dynamics_on:
            # color add/sub/transient/persistent
            alpha = 1
            cNone = (0, 0, 0, alpha)
            cSubtract = (1, 0, 0, alpha)
            cAdd = (0, 1, 0, alpha)
            cTransient = (0, 0, 1, alpha)
            cPersistent = (1, 1, 0, alpha)

            cMatrix = []

            m = self.yRunRow.shape[0]
            n = self.yRunRow.shape[1]

            for i in range(m):
                for j in range(n):
                    currColor = cNone
                    prev = 'nan'
                    next = 'nan'
                    if j > 0:
                        prev = self.sessIdx[i][j - 1] >= 0
                    if j < n - 1:
                        next = self.sessIdx[i][j + 1] >= 0
                    if not prev and j > 0:
                        currColor = cAdd
                    if not next and j < n - 1:
                        currColor = cSubtract
                    if not prev and not next and j > 0 and j < n - 1:
                        currColor = cTransient
                    if prev and next:
                        currColor = cPersistent

                    cMatrix.append(currColor)
        else:
            cMatrix = 'b'

        self.myScatterPlot.set_color(cMatrix)
        """

    def selectPoint(self, stackdbIdx):
        """Visually select a single point

        todo: extend this to take a list of points to select
        """

        ind = self.reverseLookup[stackdbIdx]
        ind = int(ind)
        if not ind >= 0:
            return
        xPnt = [self.xPlot[ind]]
        yPnt = [self.yPlot[ind]]
        if self.plotPointObj:
            self.plotPointObj.set_xdata(xPnt)
            self.plotPointObj.set_ydata(yPnt)
        else:
            # this is assuming we only plotted one line
            self.plotPointObj = self.axes.plot(xPnt, yPnt, 'yo-')[0]
        self.draw()

    def receiveevent(self, event):
        print 'mmStackPlotCanvas.receiveevent()', event.type
        if event.map != self.map:
            return
        if event.mapSession != self.stateDict['sessidx']:
            return

        if event.type == 'spine selection':
            self.selectPoint(event.stackdbIdx)

    def onkey(self, event):
        print 'mmStackPlotCanvas.onkey()', event.key
        super(mmStackPlotCanvas, self).onkey(event)

    def onpick(self, event):
        """
        Respond to clicks in a stack plot.

        event.ind: A list of hit points, just use the first.
        """

        print 'mmStackPlotCanvas.onpick()', event.ind
        ind = event.ind
        if not len(ind) >= 1:
            return

        stackdbIdx = self.stackdbIdx_plot[ind[0]]

        # transmit selection event to all open windows
        newEvent = mmEvent(self.map, self.stateDict['sessidx'], stackdbIdx)
        """
        newEvent = mmEvent()
        newEvent.type = 'spine selection'
        newEvent.map = self.map
        newEvent.mapSession = self.stateDict['sessidx']
        newEvent.stack = None
        newEvent.stackdbIdx = stackdbIdx
        newEvent.runMapRow = None # we should not have to fill this in here
        """
        self.parent.broadcastevent(newEvent)

        #statusStr = 'User Select: stackdbIdx:' + str(stackdbIdx)
        statusStr = newEvent.getText()
        self.parent.setStatus(statusStr)

    def plot(self, stateDict):
        """Plot mmStack values"""
        self.myWinType = 'stack_plot'

        #todo: get this into constructor of ALL plot window/canvas objects
        self.stateDict = stateDict

        self.map = stateDict['map']
        stack = stateDict['stack']
        xStat = stateDict['xstat']
        yStat = stateDict['ystat']
        roiType = stateDict['roitype']
        segmentID = stateDict['segmentid']

        stateDict = stack.getStackValues3(stateDict)

        self.xPlot = stateDict['x']
        self.yPlot = stateDict['y']
        self.stackdbIdx_plot = stateDict['stackidx']
        self.reverseLookup = stateDict['reverse']

        #we only get the values we are plotting here
        #self.xPlot, self.stackdbIdx_plot, self.reverseLookup = stack.getStackValues(xStat, roiType=roiType, segmentID=segmentID)
        #self.yPlot, tmp, tmp = stack.getStackValues(yStat, roiType=roiType, segmentID=segmentID)

        """
        #reverseLookup is same size as stackdb, for object i it gives us index into xPlot and yPlot
        self.reverseLookup = np.zeros(stack.numObj())
        self.reverseLookup[:] = np.NaN
        for i, val in enumerate(self.stackdbIdx_plot):
            if val >= 0:
                self.reverseLookup[val] = i
        """

        self.myScatterPlot = self.axes.scatter(self.xPlot, self.yPlot, marker='o', picker=True)

        self.axes.set_xlabel(xStat)
        self.axes.set_ylabel(yStat)

class mmStackCanvas(mmCanvas):
    """Plot and interact with a 3D images stack"""

    def __init__(self, parent=None):
        mmCanvas.__init__(self, parent=parent)

        self.sliceNumber = None

    def onscroll(self, event):
        if self.myWinType == 'stack_image':
            k = self.stack.images.shape[0]
            if event.button == 'up':
                self.sliceNumber -= 1
            elif event.button == 'down':
                self.sliceNumber += 1

            # bounds check
            if self.sliceNumber < 0:
                self.sliceNumber = 0
            elif self.sliceNumber > k - 1:
                self.sliceNumber = k - 1

            self.setSlice_(self.sliceNumber)

    def onpick(self, event):
        """
        Respond to clicks in a map, stack, and image plot.
        """

        print 'mmStackCanvas.onpick()', event.ind
        print '   ON PICK IS NOT WORKING FOR STACK IMAGE !!!!!'

        """
        event.ind is a list of hit points, just use the first.
        We are normally plotting self.runMap (a 2D nparray) with NaN.
        event.ind is index into this array AFTER nan has been stripped.
        """

        ind = event.ind
        if not len(ind) >= 1:
            return

        # self.stackdbIdx_plot is of type int, there can not be any nan with int
        # tmp = ~np.isnan(self.stackdbIdx_plot)
        stackdbIdx = self.stackdbIdxMasked[ind[0]]
        # if we are in a map, figure out runIdx? Or let the propogation function do this? Or the event class?
        # write mmStack.getObjectValue(stat) to retrieve (roiType, segmentID, x, y, z, etc)

        #self.selectPoint(stackdbIdx)

        # transmit selection event to all open windows
        newEvent = mmEvent(self.map, self.stateDict['sessidx'], stackdbIdx)
        self.parent.broadcastevent(newEvent)

        # update status bar
        statusStr = newEvent.getText()
        self.parent.setStatus(statusStr)

    def toggledynamics(self, onoff=None):
        """Need to write this for stack, see parent function"""
        pass

    def selectPoint(self, stackdbIdx, snap=True):
        """Visually select a single point

        todo: extend this to take a list of points to select
        todo: this will select points that may be masked out (we use self.xPlot/self.yPlot but are plotting self.xMasked/self.yMasked
        """

        ind = self.reverseLookup[stackdbIdx]
        ind = int(ind)
        if not ind >= 0:
            return
        xPnt = [self.xPlot[ind]]
        yPnt = [self.yPlot[ind]]
        if self.plotPointObj:
            self.plotPointObj.set_xdata(xPnt)
            self.plotPointObj.set_ydata(yPnt)
        else:
            # this is assuming we only plotted one line
            self.plotPointObj = self.axes.plot(xPnt, yPnt, 'yo-')[0]

        if snap:
            zPnt = self.zPlot[ind]
            self.setSlice_(zPnt) # call draw()
        else:
            self.draw()

    def receiveevent(self, event):
        print 'mmStackPlotCanvas.receiveevent()', event.type
        if event.map != self.map:
            return
        if event.mapSession != self.stateDict['sessidx']:
            return

        if event.type == 'spine selection':
            self.selectPoint(event.stackdbIdx)

    def plot(self, stateDict):
        """Plot a mmStack.images 3D image"""

        self.myWinType = 'stack_image'
        self.stateDict = stateDict

        self.map = stateDict['map']
        self.stack = stateDict['stack']
        self.sliceNumber = 0

        self.stack.loadStackImages(2)

        roiType = stateDict['roitype']
        segmentID = stateDict['segmentid']

        #
        #  images

        # max project
        # self.maxProject = np.amax(self.stack.images, axis=0)
        iLeft = 0
        iTop = 0
        iRight = self.stack.voxelx * self.stack.images.shape[1]  # this only handles square images
        iBottom = self.stack.voxely * self.stack.images.shape[2]  # this only handles square images
        self.imgplot = self.axes.imshow(self.stack.images[0, :, :], extent=[iLeft, iRight, iBottom, iTop])  # l, r, b, t
        self.axes.set_xlabel('um')
        self.axes.set_ylabel('um')

        print 'image is of type:', self.stack.images.dtype

        #
        #  line
        self.line_xyz = self.stack.line.getLine(segmentID)

        if self.line_xyz is not None:
            markersize = 2
            self.myLinePlot = self.axes.scatter(self.line_xyz[:, 0], self.line_xyz[:, 1], marker='.',
                                          s=markersize)  # , picker=True)

        #
        #  spines
        ystat = 'y'
        xstat = 'x'
        roiType = stateDict['roitype']

        plotDict = stateDict.copy()
        plotDict['xstat'] = 'x'
        plotDict['ystat'] = 'y'
        plotDict['zstat'] = 'z'

        plotDict = self.stack.getStackValues3(plotDict)

        self.xPlot = plotDict['x']
        self.yPlot = plotDict['y']
        self.zPlot = plotDict['z']

        self.stackdbIdx_plot = plotDict['stackidx']
        self.reverseLookup = plotDict['reverse']
        #self.xPlot, self.stackdbIdx_plot, self.reverseLookup = self.stack.getStackValues('x', roiType=roiType, segmentID=segmentID)
        #self.yPlot, tmp, tmp = self.stack.getStackValues('y', roiType=roiType, segmentID=segmentID)
        #self.zPlot, tmp, tmp = self.stack.getStackValues('z', roiType=roiType, segmentID=segmentID)

        markersize = 10
        self.myScatterPlot = self.axes.scatter(self.xPlot, self.yPlot, marker='o', s=markersize, picker=True)

        self.setSlice_(0)

        #
        # annotate
        # legendStr = self.stack.name
        # self.annotation = self.ax.annotate(legendStr, xy=(0,-20))

        # self.draw()

    def setSliceContrast(self):

        img = self.stack.images[self.sliceNumber, :, :].copy()

        maxInt = math.pow(2,16) - 1
        lowContrast = self.parent.lowContrast
        highContrast = self.parent.highContrast
        mult = maxInt / abs(highContrast - lowContrast)

        #img.astype(numpy.uint16)
        img[img < lowContrast] = lowContrast
        img[img > highContrast] = highContrast
        img -= lowContrast
        img *= int(mult)

        self.imgplot.set_data(img)

    def setSlice_(self, sliceNum):
        """Set the slice when canvas is displaying a mmStack"""
        # error check
        k = self.stack.images.shape[0]
        if sliceNum < 0:
            sliceNum = 0
        if sliceNum > k - 1:
            sliceNum = k - 1
        else:
            #
            # image
            #self.imgplot.set_data(self.stack.images[sliceNum, :, :])
            self.setSliceContrast()

            upperz = sliceNum - 5
            lowerz = sliceNum + 5

            # set_offsets() to set position of x/y scatter
            # set_array() to set color
            # for use of set_offsets, see:
            #    https://brushingupscience.wordpress.com/2016/06/21/matplotlib-animations-the-easy-way/

            #
            # stackdb points
            # We need to keep track of the mask we are plotting with so onpick ind[0] works
            try:
                self.zMask = np.ma.masked_outside(self.zPlot, upperz, lowerz)
                self.xMasked = self.xPlot[~self.zMask.mask]
                self.yMasked = self.yPlot[~self.zMask.mask]
                self.stackdbIdxMasked = self.stackdbIdx_plot[~self.zMask.mask]
            except:
                print 'ERROR: mmStackCanvas.setSlice_'

            # set_offsets must be passed an Nx2 array. Here we use np.c_[]
            self.myScatterPlot.set_offsets(np.c_[self.xMasked, self.yMasked])

            #
            # line
            if self.line_xyz is not None:
                zMask = np.ma.masked_outside(self.line_xyz[:, 2], upperz, lowerz)
                xMasked = self.line_xyz[~zMask.mask, 0]
                yMasked = self.line_xyz[~zMask.mask, 1]

                # set_offsets must be passed an Nx2 array. Here we use np.c_[]
                self.myLinePlot.set_offsets(np.c_[xMasked, yMasked])

            # legendStr = self.stack.name + ' ' + str(sliceNum) + '/' + str(k)
            # self.annotation.set_text(legendStr)

            #
            # refresh
            self.draw()
