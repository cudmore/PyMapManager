"""
Utility functions and classes for PyMapManager.
"""

#: Allowed ROI types. Specifies valid 'roiType'.
#ROI_TYPES = ['spineROI', 'otherROI']

#: Allowed stack stats. Specifies valid 'tokens' for mmStack.getValue().
'''
STACK_STATS = ['Idx',
               'x',
               'y',
               'z',
               'pDist']
'''

PLOT_DICT = {
    'map' : None, #: map (object) mmMap
    'mapname' : None,
    'sessidx' : None, #: sessIdx (int): map session
    'stack' : None, #: stack (object) use for single timepoint analysis

    'xstat' : None, #: xstat (str): Name of statistic to retreive, corresponds to column in stack.stackdb
    'ystat' : None,
    'zstat' : None,
    'roitype' : ['spineROI'], #: roiType
    'segmentid' : [],

    'stacklist' : [],   # list of int to specify sessions/stacks to plot, [] will plot all

	'getMapDynamics' : True, # set True to get map 'dynamics'
	
    'plotbad' : True,
    'plotintbad' : False,
    'showlines' : True,
    'showdynamics': True,

    #  Filled in by get functions
    'x' : None,
    'y' : None,
    'z' : None,
    'stackidx' : None,
    'reverse' : None,
    'runrow': None,
    'mapsess': None,
}

def newplotdict():
    """
    Get a new default plot dictionary.

    The plot dictionary is used to tell plot functions what to plot (e.g. ['xtat'] and ['ystat']).
    
    All plot function return the same plot dictionary with keys filled in with values that were plotted
    (e.g. ['x'] and ['y']).
    
    Example::
    
    	import pymapmanager as pmm
    	
    	path = 'PyMapManager/examples/exampleMaps/rr30a/rr30a.txt'
    	map = pmm.mmMap(path)
    	plotdict = pmm.mmUtil.newplotdict()
    	plotdict['xstat'] = 'days'
    	plotdict['ystat'] = 'pDist' # position of spine on its parent segment
    	plotdict = map.getMapValues3(plotdict)
    	
    	# display with matplotlib
    	plotdict['x']
    	plotdict['y']
    	
    """
    return PLOT_DICT.copy()

class mmEvent:
    """
    Class used by Qt to broadcast events.
    Events can be user events like 'spine selection' or program events like 'map opened'
    """

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
        """
        Make a single spine selection event

        Args:
            map (object): :class:`pymapmanager.mmMap`
            sessIdx (int): :class:`pymapmanager.mmMap` session number
            stackdbIdx (int): Annotation number in a :class:`pymapmanager.mmStack`
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