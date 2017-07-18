import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import Tkinter as Tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

class mmMapPlot():
    def __init__(self, master, theMap):
        self.master = master
        self.map = theMap

    def plot(self, xstat, ystat, segmentID=[]):
        roiType = ['spineROI']
        plotBad = False

        startTime = time.time()

        m = self.map.runMap.shape[0]
        n = self.map.runMap.shape[1]

        yPlot = np.empty([m,n])
        xPlot = np.empty([m,n])
        yPlot[:] = np.NAN
        xPlot[:] = np.NAN

        #keep track of stack centric index we are plotting
        yIdx = np.empty([m,n])
        yIdx[:] = np.NAN

        # colors = np.chararray([m,n])
        colors = [] #'k'

        for j in range(n):
            orig_df = self.map.stacks[j].stackdb

            #valid indices from runMap
            goodIdx = self.map.runMap[:,j]

            runMap_idx = orig_df.index.isin(goodIdx)

            if roiType is not None:
                roiType_idx = orig_df['roiType'].isin(roiType)
                runMap_idx = np.logical_and(runMap_idx,roiType_idx)
            if segmentID:
                segmentID_idx = orig_df['parentID'].isin(segmentID)
                runMap_idx = np.logical_and(runMap_idx, segmentID_idx)
            if not plotBad:
                notBad_idx = ~orig_df['isBad'].isin([1])
                runMap_idx = np.logical_and(runMap_idx, notBad_idx)

            final_df = orig_df.ix[runMap_idx]

            # convert to values at end
            yPlot[final_df.index,j] = final_df[ystat].values
            xPlot[final_df.index,j] = final_df[xstat].values

            #keep track of stack centric spine idx
            yIdx[final_df.index,j] = final_df.index.values

            #colors[0:mFinal,j] = 'b'

        stopTime = time.time()
        print 'mmMapPlot.plot() took', round(stopTime-startTime,2), 'seconds'

        #self.secondWindow = Tk.Toplevel()
        #plt.plot([1,2,3])

        self.fig = plt.figure()
        #self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        self.ax.scatter(xPlot,yPlot)
        #ax.ylabel(ystat)
        #ax.xlabel(xstat)

        '''
        # select a run
        seedSession = 0
        seedSpineIdx = 65
        yRun = yPlot[seedSpineIdx,:]
        xRun = xPlot[seedSpineIdx,:]
        self.ax.plot(xRun,yRun)
        '''

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.show()
        #self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        #toolbar = NavigationToolbar2TkAgg(self.canvas, self.master)
        #toolbar.update()
        #self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        self.canvas.mpl_connect('key_press_event', self.onkey)
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('scroll_event', self.onscroll)

    def plot_qt(self, xstat, ystat, segmentID=[]):
        roiType = ['spineROI']
        plotBad = False

        startTime = time.time()

        m = self.map.runMap.shape[0]
        n = self.map.runMap.shape[1]

        yPlot = np.empty([m,n])
        xPlot = np.empty([m,n])
        yPlot[:] = np.NAN
        xPlot[:] = np.NAN

        #keep track of stack centric index we are plotting
        yIdx = np.empty([m,n])
        yIdx[:] = np.NAN

        # colors = np.chararray([m,n])
        colors = [] #'k'

        for j in range(n):
            orig_df = self.map.stacks[j].stackdb

            #valid indices from runMap
            goodIdx = self.map.runMap[:,j]

            runMap_idx = orig_df.index.isin(goodIdx)

            if roiType is not None:
                roiType_idx = orig_df['roiType'].isin(roiType)
                runMap_idx = np.logical_and(runMap_idx,roiType_idx)
            if segmentID:
                segmentID_idx = orig_df['parentID'].isin(segmentID)
                runMap_idx = np.logical_and(runMap_idx, segmentID_idx)
            if not plotBad:
                notBad_idx = ~orig_df['isBad'].isin([1])
                runMap_idx = np.logical_and(runMap_idx, notBad_idx)

            final_df = orig_df.ix[runMap_idx]

            # convert to values at end
            yPlot[final_df.index,j] = final_df[ystat].values
            xPlot[final_df.index,j] = final_df[xstat].values

            #keep track of stack centric spine idx
            yIdx[final_df.index,j] = final_df.index.values

            #colors[0:mFinal,j] = 'b'

        stopTime = time.time()
        print 'mmMapPlot.plot() took', round(stopTime-startTime,2), 'seconds'


        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        self.ax.scatter(xPlot,yPlot)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.show()

        self.canvas.mpl_connect('key_press_event', self.onkey)
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('scroll_event', self.onscroll)

    def onkey(self):
        print 'onkey event'

    def onclick(self,event):
        print 'mmMapPlot.onclick()'
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            (event.button, event.x, event.y, event.xdata, event.ydata))

    def onscroll(self,event):
        print 'mmMapPlot.onscroll()'
        print 'event:', event
        #print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #    (event.button, event.x, event.y, event.xdata, event.ydata))
