"""
Helper class to plot mmMap annotations.

Example::

    from pymapmanager.mmMap import mmMap
    from pymapmanager.mmUtil import newplotdict
    %matplotlib notebook

    # load a map
    myMapFile = 'PyMapManager/examples/exampleMaps/rr30a/rr30a.txt'
    myMap = mmMap(filePath=myMapFile)

    # plot
    mp = mmMapPlot2(myMap)
    plotDict = newplotdict()
    plotDict['segmentid'] = 1 # only map segment 1
    mp.plotMap0(plotDict)
"""
from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np

class mmMapPlot2():
    def __init__(self, m):
        self.map = m
        self.myScatterPlot = None
        self.myLinePlot = None
        self.dynamics_on = False
        self.lines_on = False

        self.pd = None # plot dict

    def onclick(self, event):
        """
        Used by Qt interface.

        Args:
            event (:class:`pymapmanager.mmUtil.mmEvent`)

        """
        print('mmMapPlot2.onclick()', event.button, event.x, event.y, event.xdata, event.ydata)

    def _plotMap(self, fig):
        self.figure = fig

        # self.axes = self.figure.add_subplot(111)
        self.axes = self.figure.add_axes([0.1, 0.1, 0.9, 0.9])  # remove white border
        #self.axes.axis('off')  # turn off axis labels

        markersize = 10  # units here is area
        #self.myScatterPlot = self.axes.scatter(self.pd['x'], self.pd['y'], marker='o', s=markersize, picker=True)
        self.myScatterPlot = self.axes.scatter(self.pd['x'].flatten(), self.pd['y'].flatten(), marker='o', s=markersize, picker=True)

        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        self.axes.set_xlabel(self.pd['xstat'])
        self.axes.set_ylabel(self.pd['ystat'])

        if self.pd['showdynamics']:
            self.toggledynamics(True)
        if self.pd['showlines']:
            self.togglelines(True)

    def plotMap0(self, fig, pd):
        """
        Plot a canonical spine map of position along segment versus session.

        Args:
            fig: Either a matplotlib.figure.Figure if using Qt or
                plt.figure() if using command line or IPython/Jupyter.
            pd: A plot dictionary describing what to plot. Get default from mmUtil.newplotdict().

        Returns: None
        """

        #fig.canvas.mpl_connect('button_press_event', self.onclick)

        #self.width = 4
        #self.height = 4
        #self.dpi = 100

        # Qt has to make Figure()
        # self.figure = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        # self.canvas = FigureCanvas(self.figure)
        #self.figure = fig

        self.pd = pd
        #self.pd['plotbad'] = True
        #self.pd['getMapDynamics'] = True
        self.pd['xstat'] = 'mapSession'
        self.pd['ystat'] = 'pDist'
        self.pd['zstat'] = 'cAngle'
        self.pd = self.map.getMapValues3(pd)

        # get spine angle and offset
        offset = 0.1
        cAngle = pd['z']
        #todo: put this back in
        if 0:
            self.pd['x'][cAngle > 180] += offset
            self.pd['x'][cAngle < 180] -= offset

        self._plotMap(fig) # uses self.pd

        # text = ax.text(0, 0, "", va="bottom", ha="left")

    def plotMap(self, fig, pd):
        """
        Plot x/y values from a map.

        Args:
            fig: Either a matplotlib.figure.Figure if using Qt or
                plt.figure() if using command line or IPython/Jupyter.
            pd (dict): A plot dictionary describing what to plot. Get default from mmUtil.newplotdict().
                Fill in ['xstat'] and ['ystat'] with valid stack annotation names.

        Returns: None
        """

        #fig.canvas.mpl_connect('button_press_event', self.onclick)

        #self.width = 4
        #self.height = 4
        #self.dpi = 100

        # Qt has to make Figure()
        # self.figure = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        # self.canvas = FigureCanvas(self.figure)
        #self.figure = fig

        self.pd = self.map.getMapValues3(pd)

        self._plotMap(fig)

        """
        # self.axes = self.figure.add_subplot(111)
        self.axes = self.figure.add_axes([0, 0, 1, 1])  # remove white border
        #self.axes.axis('off')  # turn off axis labels

        markersize = 10  # units here is area
        self.myScatterPlot = self.axes.scatter(self.pd['x'], self.pd['y'], marker='o', s=markersize, picker=True)

        #self.axes.spines['top'].set_visible(False)
        #self.axes.spines['right'].set_visible(False)

        self.axes.set_xlabel(self.pd['xstat'])
        self.axes.set_ylabel(self.pd['ystat'])

        self.toggledynamics(True)
        self.togglelines(True)

        # text = ax.text(0, 0, "", va="bottom", ha="left")
        """

    @property
    def x(self):
        """
        Returns an array of x values in the plot.
        """
        return self.pd['x']

    @property
    def y(self):
        """
        Returns an array of y values in the plot.
        """
        return self.pd['y']

    def getUserSelection(self, pnt):
        """
        Return session and stackdb index when user click on a window in Qt

        Args:
            pnt: point selected in Qt canvas onpick()

        Returns: session index, stackdb index

        """
        mapsess = self.pd['mapsess']
        sessIdx_noNan = mapsess[~np.isnan(mapsess)]
        sessIdx = int(sessIdx_noNan[pnt])

        stackidx = self.pd['stackidx']
        stackdbIdx_noNan = stackidx[~np.isnan(stackidx)]
        stackdbIdx = int(stackdbIdx_noNan[pnt])

        return sessIdx, stackdbIdx

    def togglelines(self, onoff=None):
        """Toggle lines connecting annotations between timepoint. Be carefull here on repeatedly plot these lines"""

        if onoff is not None:
            self.lines_on = onoff
        else:
            self.lines_on = ~self.lines_on

        if self.lines_on:
            linewidth = 0.5
            self.myLinePlot = self.axes.plot(self.pd['x'].transpose(), self.pd['y'].transpose(), c='k',
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
            cBad = (1, 0, 1, alpha)

            colorList = []
            colorList.append(cNone)
            colorList.append(cAdd) # 1 
            colorList.append(cSubtract) # 2
            colorList.append(cTransient) # 3
            colorList.append(cPersistent) # 4
            
            m = self.pd['runrow'].shape[0]
            n = self.pd['runrow'].shape[1]

            cMatrix = []
            for i in range(m):
                for j in range(n):
                    currColor = cNone
                    currDynamics = self.pd['dynamics'][i][j].astype(int)
                    if currDynamics > 0:
                        currColor = colorList[currDynamics]
                    # bad
                    if self.pd['plotbad']:
                    	isBad = self.pd['isBad'][i][j] == 1
                    	if isBad:
                    	    #print(i, j, 'is bad')
                    	    currColor = cBad
                    
                    # nan values (no spine) in our scatter don't get plotted by matplotlib
                    if self.pd['dynamics'][i][j] >= 0:
                        cMatrix.append(currColor)
        else:
            cMatrix = 'b'

        self.myScatterPlot.set_color(cMatrix)
        #self.myScatterPlot.set_color(ijList)


