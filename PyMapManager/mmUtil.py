"""Utility functions and classes for map manager.

Try and keep these out of __init__.py
"""

ROI_TYPES = ['spineROI', 'otherROI']
"""
Allowed ROI types. Specifies valid 'roiType'.
"""

STACK_STATS = ['Idx',
               'x',
               'y',
               'z',
               'pDist']
"""
Allowed stack stats. Specifies valid 'tokens' for mmStack.getValue().
"""

PLOT_STRUCT = dict()
"""
Used to read interface state in QT and used to reduce number of parameters passed to plot functions
"""
PLOT_STRUCT['xstat'] = ''
PLOT_STRUCT['ystat'] = ''
PLOT_STRUCT['roiType'] = 'spineROI'
PLOT_STRUCT['segmentID'] = [] # all segment
PLOT_STRUCT['plotBad'] = False
PLOT_STRUCT['plotIntBad'] = False

def newplotstruct(): return PLOT_STRUCT.copy()

class mmEvent:
    """Class to broadcast events. Events can be user events like 'spine selection' or program events like 'map opened'"""

    def __init__(self, map, sessIdx, stackdbIdx):
        self.type = ''  # unique string identifying the event
        self.map = None  # object
        self.mapSession = None  # index into mmMap.stacks
        self.stack = None  # object
        self.stackdbIdx = None  # stack centric index into stack.stackdb
        self.runMapRow = None

        if map and sessIdx>=0 and stackdbIdx >= 0:
            self.spineSelection(map, sessIdx, stackdbIdx)

    def spineSelection(self, map, sessIdx, stackdbIdx):
        """Make a single spine selection event

        map: map object
        sessIdx: int
        stackdbIdx: int

        Todo: extend this to list of spines
        """

        self.type = 'spine selection'
        self.map = map
        self.mapSession = sessIdx
        self.stack = self.map.stacks[sessIdx]
        self.stackdbIdx = stackdbIdx
        runMapRowIdx = 6 #xxx
        self.runMapRow = map.objMap[runMapRowIdx,stackdbIdx,sessIdx]
        self.runMapRow = int(self.runMapRow)

    def getText(self):
        """Get a
        """
        ret = 'User Select: sess:' + str(self.mapSession) + ' stackdbIdx:' + str(self.stackdbIdx) + ' runRow:' + str(
            self.runMapRow)
        return ret