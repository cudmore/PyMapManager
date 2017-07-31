"""
A mmMap is a time-series of :class:`PyMapManager.mmStack` plus some book-keeping to link corresponding annotations
between stacks and to link corresponding line segments between stacks.

Details::

	stacks: list of :class:`PyMapManager.mmStack`
"""

import os, time, copy
from glob import glob # for pool
import pandas as pd
import numpy as np

#import PyMapManager
from PyMapManager.mmUtil import ROI_TYPES, newplotdict
from PyMapManager.mmStack import mmStack

#import logging
#logging.basicConfig(filename='example.log',level=logging.DEBUG)

'''3D numpy array, rows are stack centric indices, columns are sessions, 3rd dimension is:
    [0] idx, [1] next, [2] nextTP, [3] prev, [4] prevTP
    [5] blank, [6] runIdx, [7] dynType, [8] forced
    [9] nodeType, [10] segmentID, [11] splitIdx
'''

class mmMap():
	"""
	Args:
		filePath (str): Full file path to .txt file for the map. File is inside map folder, for map a5n it is /a5n/a5n.txt

	Example::

		from PyMapManager.mmMap import mmMap
		file = '/Users/cudmore/Desktop/data/rr30a/rr30a.txt'
		m = mmMap(filePath=path)

	Once created and populated with stack, get the ith mmStack using::

		stack = m.stacks[i]

	Use getMapValues2() to retrieve stack annotations (for the given segmentID) across the entire map::

		pDist_values = m.getMapValues2('pDist', segmentID=[3])
	"""

	def __init__(self, filePath=''):

		#logging.debug('mmMap.__init__() filePath:' + filePath)
		#self.log = logging.getLogger(self.__class__.__name__)
		#self.log.info("constructor")

		self.defaultRoiType = 'spineROI'

		startTime = time.time()

		if not os.path.isfile(filePath):
			print 'mmMap() error, file not found:', filePath
			return

		self.filePath = filePath #  Path to file used to open map."""
		self.folder = os.path.dirname(filePath) + '/' #  Path to enclosing folder, ends in '/'.
		self.name = os.path.basename(filePath).strip('.txt')  #  Name of the map, for a map loaded with file a5n.txt, the name is a5b. Same as enclosing folder name.
		self.table = pd.read_table(filePath, index_col=0) #  Pandas df loaded from filePath. Get values using getValue(name,session)
		self.numChannels = int(self.getValue('numChannels', 0)) #:  Number of image channels in each stack (must be the same for all stacks).
		self.numSessions = int(self.table.loc['hsStack'].count()) #:  Number of sessions in the map.

		# objMap (3d)
		objMapFile = self.folder + self.name + '_objMap.txt'
		with open(objMapFile, 'rU') as f:
			header = f.readline().rstrip()
			if header.endswith(';'):
				header = header[:-1]
			header = header.split(';')
			d = dict(s.split('=') for s in header)
			numRow = int(d['rows'])
			numCol = int(d['cols'])
			numBlock = int(d['blocks'])
		self.objMap = np.loadtxt(objMapFile, skiprows=1)
		self.objMap.resize(numBlock,numRow,numCol)

		self.runMap = self._buildRunMap(self.objMap)

		# segMap (3d)
		segMapFile = self.folder + self.name + '_segMap.txt'
		with open(segMapFile, 'rU') as f:
			header = f.readline().rstrip()
			if header.endswith(';'):
				header = header[:-1]
			header = header.split(';')
			d = dict(s.split('=') for s in header)
			numRow = int(d['rows'])
			numCol = int(d['cols'])
			numBlock = int(d['blocks'])
		self.segMap = np.loadtxt(segMapFile, skiprows=1)
		self.segMap.resize(numBlock,numRow,numCol)

		self.segRunMap = self._buildRunMap(self.segMap)

		#load each stack db
		self._stacks = [] #  A list of mmStack
		for i in range(0, self.numSessions):
			stack = mmStack(name=self._getStackName(i), numChannels=self.numChannels, map=self, mapSession=i)

			#numObj = stack.numObj()

			self.stacks.append(stack)

			#all stackdb into single pandas dataframe
			#need to offset (next, prev)

			#add nearest neighbor analysis?


		stopTime = time.time()
		print 'map', self.name, 'loaded in', round(stopTime-startTime,2), 'seconds.'

	@property
	def stacks(self):
		"""
		List of :class:`PyMapManager.mmStack` in the map.
		"""
		return self._stacks

	def __str__(self):
		objCount = 0
		for stack in self.stacks:
			objCount += stack.numObj
		return ('map:' + self.name
			+ ' segments:' + str(self.getNumSegments())
			+ ' stacks:' + str(self.numSessions)
			+ ' total object:' + str(objCount))

	def __iter__(self):
		i = 0
		while i < len(self.stacks):
			yield self.stacks[i]
			i += 1

	def getValue(self, name, sessionNumber):
		"""
		Get a value from the map (not from a stack!).

		Args:
		    name: Name of map stat
		    sessionNumber: Session number

		Returns:
		    Str (this is a single value)

		Examples::

		    m.getValue('voxelx', 5) # get the x voxel size of stack 5 (in um/pixel)
		    m.getValue('hsStack',3) # get the name of stack 3
		"""
		return self.table.loc[name].iloc[sessionNumber] # .loc specifies row, .iloc specifies a column

	def _getStackName(self, sessIdx):
		# get the name of the stack at session sessIdx, this is contained in the map header
		ret = self.getValue('hsStack', sessIdx)
		if ret.endswith('_ch1'):
			ret = ret[:-4]
		return ret

	def getMapValues3(self, pd):
		"""

		Args:
		    pd (dict): Fill in mmUtil.PLOT_DICT

		Returns pd with::

			pd['x']: 2D ndarray of xstat values, rows are runs, cols are sessions, nan is where there is no stackdb annotation
			pd['y']: same
			pd['z']: same
		"""
		startTime = time.time()

		m = self.runMap.shape[0]
		n = self.runMap.shape[1]

		if pd['xstat']:
			pd['x'] = np.empty([m, n])
			pd['x'][:] = np.NAN
		if pd['ystat']:
			pd['y'] = np.empty([m, n])
			pd['y'][:] = np.NAN
		if pd['zstat']:
			pd['z'] = np.empty([m, n])
			pd['z'][:] = np.NAN

		# keep track of stack centric index we are plotting
		yIdx = np.empty([m, n])
		yIdx[:] = np.NAN

		# keep track of session index
		ySess = np.empty([m, n])
		ySess[:] = np.NAN

		# keep track of run map rows (we already know the session/column)
		yRunRow = np.empty([m, n])
		yRunRow[:] = np.NAN

		runIdxDim = 6

		if pd['stacklist'] is not None and len(pd['stacklist'])>0:
			myRange = pd['stacklist']
		else:
			myRange = range(n)

		for j in myRange:
			orig_df = self.stacks[j].stackdb

			currSegmentID = []
			if pd['segmentid']:
				currSegmentID = self.segRunMap[pd['segmentid'], j]  # this only works for one segment -- NOT A LIST
				currSegmentID = currSegmentID.tolist()
			if pd['segmentid'] and not currSegmentID:
				# this session does not have segmentID that match
				break

			goodIdx = self.runMap[:, j]  # valid indices from runMap

			runMap_idx = orig_df.index.isin(goodIdx)  # series of boolean (Seems to play nice with nparray)

			if pd['roitype']:
				roiType_idx = orig_df['roiType'].isin(pd['roitype'])
				runMap_idx = runMap_idx & roiType_idx
			if currSegmentID:
				segmentID_idx = orig_df['parentID'].isin(currSegmentID)
				runMap_idx = runMap_idx & segmentID_idx
			if not pd['plotbad']:
				notBad_idx = ~orig_df['isBad'].isin([1])
				runMap_idx = runMap_idx & notBad_idx

			# final_df = orig_df.loc[runMap_idx]
			final_df = orig_df.ix[runMap_idx]

			### final_df.index is giving repeats -->> causing finalRows to be missing 44 and has 45 repeated 4 times
			finalIndexList = final_df.index.tolist()

			# #we have a list of valid stack centric index in runMap_idx
			# reverse this back into run centric to set rows in runMap (xPlot, yPlot)
			# finalRows = self.objMap[runIdxDim,final_df.index,j]
			finalRows = self.objMap[runIdxDim, finalIndexList, j]
			finalRows = finalRows.astype(int)

			# convert to values at end
			try:
				if pd['xstat']:
					pd['x'][finalRows, j] = final_df[pd['xstat']].values
				if pd['ystat']:
					pd['y'][finalRows, j] = final_df[pd['ystat']].values
				if pd['zstat']:
					pd['z'][finalRows, j] = final_df[pd['zstat']].values
			except KeyError, e:
				print 'getMapValues3() KeyError - reason "%s"' % str(e)

			# keep track of stack centric spine idx
			yIdx[finalRows, j] = final_df.index.values
			ySess[finalRows, j] = j
			yRunRow[finalRows, j] = finalRows  # final_df.index

		stopTime = time.time()
		print 'mmMap.getMapValues3() took', round(stopTime - startTime, 2), 'seconds'

		pd['stackidx'] = yIdx
		pd['mapsess'] = ySess
		pd['runrow'] = yRunRow
		return pd

	def getMapValues2(self, stat, roiType=['spineROI'], segmentID=[], plotBad=False, plotIntBad=False):
		"""
		Get values of a stack statistic across all stacks in the map

		Args:
		    stat (str): The stack statistic to get (corresponds to a column in mmStack.stackdb)
			roiType (str): xxx
			segmentID (list): xxx
			plotBad (boolean): xxx

		Returns:
		    2D numpy array of stat values. Each row is a run of objects connected across sessions,
		    columns are sessions, each [i][j] is a stat value
		"""

		if roiType not in ROI_TYPES:
			errStr = 'error: mmMap.getMapValues2() stat "' + stat + '" is not in ' + ROI_TYPES
			raise ValueError(errStr)

		plotDict = newplotdict()
		plotDict['roitype'] = roiType
		plotDict['xstat'] = stat
		plotDict['segmentid'] = segmentID
		plotDict['plotbad'] = plotBad
		plotDict['plotIntBad'] = plotIntBad

		plotDict = self.getMapValues3(plotDict)

		return plotDict['x']

	def getNumSegments(self):
		"""Get the number of map line segments."""
		numSegments = self.segRunMap.shape[0]
		return numSegments

	def _buildRunMap(self, theMap):
		"""Internal function. Converts 3D objMap into a 2D run map. A run map must be float as it uses np.NaN

		Args:
		    theMap: Either self.objMap or self.segMap

		Returns:
			A numpy ndarray run map
		"""

		idx = 0
		next = 1
		#nexttp = 2
		prev = 3
		#prevtp = 4
		runIdx = 6 #if this is correct we can build really fast
		m = theMap.shape[1]
		n = theMap.shape[2]
		k = theMap.shape[0]
		numRows = np.count_nonzero(~np.isnan(theMap[idx,:,0]))
		retRunMap = np.empty([numRows,n]) #, dtype=int)
		retRunMap[:] = 'nan'

		emptyRow = np.empty([1, n])
		emptyRow[:] = 'nan'

		currRow = 0
		for j in range(0,n): #sessions
			for i in range(0,m):
				#retRunMap[i,j] = 'nan'
				if theMap[idx,i,j]>=0:
					pass
				else:
					break
				if j==0:
					currRow = i
					retRunMap[currRow, j] = i
				elif not (theMap[prev,i,j]>=0):
					currRow += 1
					retRunMap = np.vstack([retRunMap, emptyRow])
					retRunMap[currRow, j] = i
					#retRunMap[retRunMap.size[0]-1,:] = 'nan'
				else:
					continue
				#retRunMap[currRow,j] = i
				nextNode = theMap[next,i, j]
				for k in range(j+1,n):
					if nextNode >= 0:
						retRunMap[currRow,k] = nextNode
					else:
						break
					nextNode = theMap[next,int(nextNode),k]
		return retRunMap

	def _getSegmentID(self, segmentNumber, sessIdx):
		"""
		Given a map centric segment index (row in segRunMap), tell us the stack centric segmentID for session sessIdx

		Args:
		    segmentNumber (int): Map centric segment index, row in segRunMap
		    sessIdx (int): Session number

		Returns: int: stack centric segmentID or nan if no corresponding segment in that session
		"""
		return self.segRunMap[segmentNumber][sessIdx] # can be nan


######################################################################
class mmMapPool():
    """
    Load all maps in a folder.

    Args:
        path (str): Full path to a folder. This folder should contain folders of maps.

    Example::

        path = '/Users/cudmore/MapManagerData/richard/Nancy/'
        maps = mmMapPool(path)
        for map in maps:
            print map
    """

    def __init__(self, path):
        self._maps = []

        startTime = time.time()

        if os.path.isdir(path):
            folders = glob(path+'/*/')
            for folder in folders:
                mapName = os.path.basename(folder[:-1])
                mapFile = folder + mapName + '.txt'
                if os.path.isfile(mapFile):
                    print 'mmMapPool() loading map:', mapName
                    map = mmMap(mapFile)
                    self.maps.append(map)
        else:
            print 'error: mmMapPool() did not find path:', path

        stopTime = time.time()
        print 'mmMapPool() loaded', len(self.maps), 'maps in', stopTime-startTime, 'seconds.'

    @property
    def maps(self):
        """
        List of :class:`PyMapManager.mmMap` in the mmMapPool.
        """
        return self._maps

    def __iter__(self):
        i = 0
        while i < len(self.maps):
            yield self.maps[i]
            i+=1

    def __str__(self):
        count = 0
        for map in self:
            for stack in map:
                count += stack.numObj
        return ('pool:'
                + ' num maps:' + str(len(self.maps))
                + ' num obj:' + str(count))
