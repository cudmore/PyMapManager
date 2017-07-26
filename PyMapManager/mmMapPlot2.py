
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


class mmMapPlot2():
    def __init__(self, m):
        self.map = m
        self.myScatterPlot = None
        self.dynamics_on = False
        self.pd = None

    def onclick(self, event):
        print 'mmMapPlot2.onclick()', event.button, event.x, event.y, event.xdata, event.ydata

    def plotMap0(self, fig, pd):
        fig.canvas.mpl_connect('button_press_event', self.onclick)

        self.width = 4
        self.height = 4
        self.dpi =  100

        # Qt has to make Figure()
        #self.figure = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        #self.canvas = FigureCanvas(self.figure)
        self.figure = fig

        self.pd = self.map.getMapValues3(pd)

        # get spine angle and offset
        offset = 0.1
        cAngle = self.map.getMapValues2('cAngle', segmentID=pd['segmentid'])
        self.pd['x'][cAngle > 180] += offset
        self.pd['y'][cAngle < 180] -= offset

        #self.axes = self.figure.add_subplot(111)
        self.axes = self.figure.add_axes([0, 0, 1, 1]) #remove white border
        self.axes.axis('off') #turn off axis labels

        markersize = 10  # units here is area
        self.myScatterPlot = self.axes.scatter(self.pd['x'], self.pd['y'], marker='o', s=markersize, picker=True)

        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        self.axes.set_xlabel(self.pd['xstat'])
        self.axes.set_ylabel(self.pd['ystat'])

        self.toggledynamics(True)

        #text = ax.text(0, 0, "", va="bottom", ha="left")

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

            m = self.pd['runrow'].shape[0]
            n = self.pd['runrow'].shape[1]

            for i in range(m):
                for j in range(n):
                    currColor = cNone
                    prev = 'nan'
                    next = 'nan'
                    if j > 0:
                        prev = self.pd['mapsess'][i][j - 1] >= 0
                    if j < n - 1:
                        next = self.pd['mapsess'][i][j + 1] >= 0
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


