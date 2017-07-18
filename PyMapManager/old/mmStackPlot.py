import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class mmStackPlot():
    def __init__(self, theStack):
        """

        :param theStack:
        """
        self.stack = theStack
        self.sliceNum = 0

    def plot(self,ystat, xstat, roiType='spineROI', segmentID=[]):
        """

        :param ystat:
        :param ytype: ['stackdb', 'ch1', 'ch2']
        :param xstat:
        :param xtype:
        :param roiType:
        :return:
        """
        print 'mmStackPlot.plot()', ystat, xstat, roiType, segmentID

        y = self.stack.getStackValues(ystat, roiType=roiType, segmentID=segmentID)
        x = self.stack.getStackValues(xstat, roiType=roiType, segmentID=segmentID)
        plt.plot(x,y,'o')
        plt.ylabel(ystat)
        plt.xlabel(xstat)
        plt.show()

    def setSlice(self,sliceNum):

        # error check
        k = self.stack.images.shape[0]
        if sliceNum<0:
            sliceNum = 0
        if sliceNum>k-1:
            sliceNum = k-1
        else:
            #
            # image
            self.imgplot.set_data(self.stack.images[sliceNum,:,:])

            upperz = sliceNum - 5
            lowerz = sliceNum +5

            #
            # stackdb
            #y = self.stack.getValues('y', roiType='spineROI', segmentID=self.segmentID)
            #y /= self.stack.voxely
            #x = self.stack.getValues('x', roiType='spineROI', segmentID=self.segmentID)
            #x /= self.stack.voxely
            #z = self.stack.getValues('z', roiType='spineROI', segmentID=self.segmentID)

            zMask = np.ma.masked_outside(self.z, upperz, lowerz)
            yMasked = self.y[~zMask.mask]
            xMasked = self.x[~zMask.mask]

            self.stackdbPlot.set_ydata(yMasked)
            self.stackdbPlot.set_xdata(xMasked)

            #
            # line
            zMask = np.ma.masked_outside(self.line_xyz[:,2], upperz, lowerz)
            yMasked = self.line_xyz[~zMask.mask,1]
            xMasked = self.line_xyz[~zMask.mask,0]
            self.linePlot.set_ydata(yMasked)
            self.linePlot.set_xdata(xMasked)

            legendStr = self.stack.name + ' ' + str(sliceNum) + '/' + str(k)
            self.annotation.set_text(legendStr)

            #
            # refresh
            #plt.show()
            self.fig.canvas.draw()

    def plotStack(self, master, segmentID=[]):
        """
        Plot the stack as an image and overlay objects and lines
        :param segmentID:
        :return:
        """
        self.segmentID = segmentID
        self.sliceNum = 0
        print 'mmStackPlot.plotStack(), slice:', self.stack.name, self.sliceNum

        # to do:
        # for now image is in pixels, we need to convert spineROI (x,y) from um to pixel

        #plt.ion()

        self.fig = plt.figure(frameon=False)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis('off')

        #
        #  images

        # max project
        self.maxProject = np.amax(self.stack.images, axis=0)
        self.imgplot = self.ax.imshow(self.maxProject)

        #this shows one image
        #self.imgplot = plt.imshow(self.stack.images[sliceNum,:,:])

        #
        #  line
        self.line_xyz = self.stack.line.getLine(segmentID)

        self.line_xyz[:,0] /= self.stack.voxelx
        self.line_xyz[:,1] /= self.stack.voxely

        self.linePlot, = self.ax.plot(self.line_xyz[:,0],self.line_xyz[:,1],'g.')

        #
        #  spines
        ystat = 'y'
        xstat = 'x'
        roiType = 'spineROI'

        self.y = self.stack.getStackValues(ystat, roiType=roiType, segmentID=segmentID)
        self.x = self.stack.getStackValues(xstat, roiType=roiType, segmentID=segmentID)
        self.z = self.stack.getStackValues('z', roiType=roiType, segmentID=segmentID)

        # convert um to pixel
        self.y /= self.stack.voxely
        self.x /= self.stack.voxelx

        self.stackdbPlot, = self.ax.plot(self.x,self.y,'yo', picker=2)
        #plt.ylabel(ystat)
        #plt.xlabel(xstat)

        #
        #annotate
        legendStr = self.stack.name
        self.annotation = self.ax.annotate(legendStr, xy=(0,-20))

        #self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.mpl1 = self.fig.canvas.mpl_connect('scroll_event', self.onscroll)
        self.mpl2 = self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.mpl3 = self.fig.canvas.mpl_connect('key_press_event', self.onkey)

        '''
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.draw()
        self.canvas.show()
        '''

        plt.show()

    def onkey(self,event):
        print 'mmStackPlot.onkey()', event.key
        key = event.key
        if key == '1':
            print '   -->> channel 1'
        elif key == '2':
            print '   -->> channel 2'
        elif key == '+':
            print '   --->> zoom in', event.x, event.y
        elif key == '-':
            print '   --->> zoom out', event.x, event.y
        elif key == 'enter':
            print '   --->> reset zoom'

    def onpick(self, event):
        # todo: we need to take mask into account, event.ind is NOT stackdb row !!!
        print 'mmStackPlot.onpick()', 'event.ind:', event.ind, self.stack.stackdb.iloc[event.ind]['roiType'].values
        #ind = event.ind
        #print('onpick3 scatter:', ind, np.take(x, ind), np.take(y, ind))

    def onclick(self,event):
        print 'mmStackPlot.onclick() event:', event
        #print('mmStackPlot.onclick() button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #    (event.button, event.x, event.y, event.xdata, event.ydata))

    def onscroll(self,event):
        #print 'mmStackPlot.onscroll() event:', event
        if event.button == 'down':
            self.sliceNum += 1
        elif event.button == 'up':
            self.sliceNum -= 1
        #bounds check
        if self.sliceNum<0:
            self.sliceNum = 0
        k = self.stack.images.shape[0]
        if self.sliceNum>k-1:
            self.slicNum = k

        self.setSlice(self.sliceNum)