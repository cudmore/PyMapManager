"""
Utility functions and classes for PyMapManager.
"""

#: Allowed ROI types. Specifies valid 'roiType'.
ROI_TYPES = ['spineROI', 'otherROI']

#: Allowed stack stats. Specifies valid 'tokens' for mmStack.getValue().
STACK_STATS = ['Idx',
               'x',
               'y',
               'z',
               'pDist']

#: Used to read interface state in QT and used to reduce number of parameters passed to plot functions
PLOT_STRUCT = dict()
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

        Args:
            map (object): :class:`PyMapManager.mmMap`
            sessIdx (int): :class:`PyMapManager.mmMap` session number
            stackdbIdx (int): Annotation number in a :class:`PyMapManager.mmStack`
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
        """
        Returns a human readable string describing the event.

        For example: 'Users Select sess:3 stackdbIdx:2, runRow:58'
        """
        ret = 'User Select: sess:' + str(self.mapSession) + ' stackdbIdx:' + str(self.stackdbIdx) + ' runRow:' + str(
            self.runMapRow)
        return ret