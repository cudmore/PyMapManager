import os, io, time, math
from errno import ENOENT
import pandas as pd
import numpy as np

from pymapmanager.mmUtil import ROI_TYPES, newplotdict
from pymapmanager.mmStack import mmStack
from pymapmanager.mmio import mmio

'''3D numpy array, rows are stack centric indices, columns are sessions, 3rd dimension is:
	[0] idx, [1] next, [2] nextTP, [3] prev, [4] prevTP
	[5] blank, [6] runIdx, [7] dynType, [8] forced
	[9] nodeType, [10] segmentID, [11] splitIdx
'''

class mmMap():
	"""
	A time-series of :class:`pymapmanager.mmStack` plus some book-keeping to link corresponding annotations
	and segments between stacks.

	Args:
		filePath (str): Full file path to .txt file for the map. File is inside map folder, for map a5n it is /a5n/a5n.txt
		urlmap (str): Name of the map to load from a :class:`pymapmanager.mmio` online repository.

	Example::

		from pymapmanager.mmMap import mmMap
		file = '/Users/cudmore/Desktop/data/cudmore/rr30a/rr30a.txt'
		m = mmMap(filePath=path)

		# Get the 3rd mmStack using
		stack = m.stacks[3]

		# Use getMapValues2() to retrieve stack annotations (for the given segmentID) across the entire map
		pDist_values = m.getMapValues2('pDist', segmentID=[3])
	"""

	def __init__(self, filePath=None, urlmap=None):
		startTime = time.time()

		self.filePath = ''
		# Full file path to .txt file for the map.

		self._folder = ''
		# Path to enclosing folder, ends in '/'.

		self.name = ''
		# Name of the map. For a map loaded with file a5n.txt, name is a5b. Same as enclosing folder name.
		# If urlmap then this is the name of the map to fetch from a :class:`pymapmanager.mmio` server.

		self.table = None
		# Pandas dataframe loaded from .txt file filePath or 'header' if using :class:`pymapmanager.mmio`.
		# Get values from this dataframe using getValue(name,sessionNumber)

		self.defaultRoiType = 'spineROI'

		self.server = None
		# Pointer to :class:`pymapmanager.mmio` server connection.
		# Only used to load from urlmap.

		self.objMap = None
		# 2D array where each row is a run of annotations.
		# objMap[i][j] gives us a mmStack centric index into mmStack.stackdb.

		self.segMap = None
		# 2D array where each row is a run of segments.
		# segMap[i][j] gives us mmStack centric index into mmStack._line

		doFile = True
		if filePath is not None:
			if not os.path.isfile(filePath):
				raise IOError(ENOENT, 'mmMap did not find filePath:', filePath)
			self.filePath = filePath #  Path to file used to open map."""
			self._folder = os.path.dirname(filePath) + '/'
			self.name = os.path.basename(filePath).strip('.txt')
			self.table = pd.read_table(filePath, index_col=0)
		elif urlmap is not None:
			doFile = False
			# try loading from url
			self.name = urlmap
			self.server = mmio.mmio()
			tmp = self.server.getfile('header', self.name)
			self.table = pd.read_table(io.StringIO(tmp.decode('utf-8')), index_col=0)

		###############################################################################
		# objMap (3d)
		if doFile:
			objMapFile = self._folder + self.name + '_objMap.txt'
			if not os.path.isfile(objMapFile):
				raise IOError(ENOENT, 'mmMap did not find objMapFile:', objMapFile)
			with open(objMapFile, 'rU') as f:
				header = f.readline().rstrip()
			self.objMap = np.loadtxt(objMapFile, skiprows=1)
		else:
			tmp = self.server.getfile('objmap', self.name)
			header = tmp.split('\n')[0]
			self.objMap = np.loadtxt(tmp.split('\n'), skiprows=1)

		if header.endswith(';'):
			header = header[:-1]
		header = header.split(';')
		d = dict(s.split('=') for s in header)
		numRow = int(d['rows'])
		numCol = int(d['cols'])
		numBlock = int(d['blocks'])

		self.objMap.resize(numBlock,numRow,numCol)
		self.runMap = self._buildRunMap(self.objMap)

		###############################################################################
		# segMap (3d)
		header = None
		if doFile:
			segMapFile = self._folder + self.name + '_segMap.txt'
			if not os.path.isfile(segMapFile):
				raise IOError(ENOENT, 'mmMap did not find segMapFile:', segMapFile)
			with open(segMapFile, 'rU') as f:
				header = f.readline().rstrip()
			self.segMap = np.loadtxt(segMapFile, skiprows=1)
		else:
			tmp = self.server.getfile('segmap', self.name)
			#header = tmp.split('\r')[0] # works when server is running on OSX
			header = tmp.split('\n')[0]
			self.segMap = np.loadtxt(tmp.split('\n'), skiprows=1)

		if header is not None:
			if header.endswith(';'):
				header = header[:-1]
			header = header.split(';')
			d = dict(s.split('=') for s in header)
			numRow = int(d['rows'])
			numCol = int(d['cols'])
			numBlock = int(d['blocks'])

			self.segMap.resize(numBlock,numRow,numCol)
			self.segRunMap = self._buildRunMap(self.segMap)

		###############################################################################
		#load each stack db
		self._stacks = [] #  A list of mmStack
		for i in range(0, self.numSessions):
			if doFile:
				stack = mmStack(name=self._getStackName(i), numChannels=self.numChannels, \
								map=self, mapSession=i)
			else:
				stack = mmStack(name=self._getStackName(i), numChannels=self.numChannels, \
								map=self, mapSession=i, urlmap=self.name)
			self.stacks.append(stack)

		stopTime = time.time()
		print 'map', self.name, 'loaded in', round(stopTime-startTime,2), 'seconds.'

	@property
	def numChannels(self):
		"""
		Number of image channels in each stack (must be the same for all stacks).
		"""
		return int(self.getValue('numChannels', 0))

	@property
	def numSessions(self):
		"""
			Number of sessions (timepoints) in the map (time-series).
		"""
		return int(self.table.loc['hsStack'].count())

	@property
	def stacks(self):
		"""
		List of :class:`pymapmanager.mmStack` in the map.
		"""
		return self._stacks

	@property
	def numMapSegments(self):
		"""The number of line segments in the map.
		Corresponding segments are connected together with the segMap.
		"""
		numSegments = self.segRunMap.shape[0]
		return numSegments

	def __str__(self):
		objCount = 0
		for stack in self.stacks:
			objCount += stack.numObj
		return ('map:' + self.name
			+ ' map segments:' + str(self.numMapSegments)
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
			name: Name of map value
			sessionNumber: Session number of the stack

		Returns:
			Str (this is a single value)

		Examples::

			m.getValue('pixelsz', 2) # get the number of z-slices (pixels) of stack 2.
			m.getValue('voxelx', 5) # get the x voxel size of stack 5 (in um/pixel).
			m.getValue('hsStack',3) # get the name of stack 3.
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
		Get values of a stack annotation across all stacks in the map.

		Args:
			pd (dict): A plot dictionary describing what to plot. Get default from mmUtil.newplotdict().

		Returns:

			| pd['x'], 2D ndarray of xstat values, rows are runs, cols are sessions, nan is where there is no stackdb annotation
			| pd['y'], same
			| pd['z'], same
			| pd['stackidx'], Each [i]j[] gives the stack centric index of annotation value at [i][j].
			| pd['mapsess'], Each [i][j] gives the map session of value at annotation [i][j].
			| pd['runrow'],

		"""
		startTime = time.time()

		# make sure pd['roitype'] is a list
		if not isinstance(pd['roitype'], list):
			pd['roitype'] = [pd['roitype']]

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

		# keep track of map segment id
		yMapSegment = np.empty([m, n])
		yMapSegment[:] = np.NAN

		runIdxDim = 6

		if pd['stacklist'] is not None and len(pd['stacklist'])>0:
			myRange = pd['stacklist']
		else:
			myRange = range(n)

		for j in myRange:
			orig_df = self.stacks[j].stackdb

			currSegmentID = []
			if self.numMapSegments:
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

			finalIndexList = final_df.index.tolist()

			# we have a list of valid stack centric index in runMap_idx
			# reverse this back into run centric to set rows in runMap (xPlot, yPlot)
			# finalRows = self.objMap[runIdxDim,final_df.index,j]
			finalRows = self.objMap[runIdxDim, finalIndexList, j]
			finalRows = finalRows.astype(int)

			#print 'getMapValues3() final_df:', final_df

			# convert to values at end
			try:
				if pd['xstat'] and pd['xstat'] != 'session':
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

			# 20171119 finish this
			#print 'a', final_df['parentID'].values.astype(int)
			#print 'b', self.segMap[0, final_df['parentID'].values.astype(int), j]
			yMapSegment[finalRows, j] = self.segMap[0, final_df['parentID'].values.astype(int), j]

			if pd['xstat'] == 'session':
				#print 'swapping x for session'
				pd['x'][finalRows, j] = j #ySess[finalRows,j]

		# strip out a nan rows, can't do this until we have gone through all sessions
		# makes plotting way faster
		ySess = ySess[~np.isnan(yIdx).all(axis=1)]
		yRunRow = yRunRow[~np.isnan(yIdx).all(axis=1)]
		if pd['xstat']:
			pd['x'] = pd['x'][~np.isnan(yIdx).all(axis=1)]
		if pd['ystat']:
			pd['y'] = pd['y'][~np.isnan(yIdx).all(axis=1)]
		if pd['zstat']:
			pd['z'] = pd['z'][~np.isnan(yIdx).all(axis=1)]
		yIdx = yIdx[~np.isnan(yIdx).all(axis=1)] # do this last

		stopTime = time.time()
		print 'mmMap.getMapValues3() took', round(stopTime - startTime, 2), 'seconds'

		pd['stackidx'] = yIdx
		pd['mapsess'] = ySess
		pd['runrow'] = yRunRow
		pd['mapsegment'] = yMapSegment

		#print pd['x']
		#print pd['y']

		return pd

	def getMapValues2(self, stat, roiType=['spineROI'], segmentID=[], plotBad=False, plotIntBad=False):
		"""
		Get values of a stack annotation across all stacks in the map.

		Args:
			stat (str): The stack annotation to get (corresponds to a column in mmStack.stackdb)
			roiType (str): xxx
			segmentID (list): xxx
			plotBad (boolean): xxx

		Returns:
			2D numpy array of stat values. Each row is a run of objects connected across sessions,
			columns are sessions, each [i][j] is a stat value
		"""

		#if roiType not in ROI_TYPES:
		#	errStr = 'error: mmMap.getMapValues2() stat "' + roiType + '" is not in ' + ','.join(ROI_TYPES)
		#	raise ValueError(errStr)

		plotDict = newplotdict()
		plotDict['roitype'] = roiType
		plotDict['xstat'] = stat
		plotDict['segmentid'] = segmentID
		plotDict['plotbad'] = plotBad
		plotDict['plotIntBad'] = plotIntBad

		plotDict = self.getMapValues3(plotDict)

		return plotDict['x']

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

	def _getStackSegmentID(self, mapSegmentNumber, sessIdx):
		"""
		Given a map centric segment index (row in segRunMap), tell us the stack centric segmentID for session sessIdx

		Args:
			mapSegmentNumber (int): Map centric segment index, row in segRunMap
			sessIdx (int): Session number

		Returns: int or nan: Stack centric segmentID or None if no corresponding segment in that session.
		"""
		stackSegment = np.nan
		if self.segRunMap is not None:
			stackSegment = self.segRunMap[mapSegmentNumber][sessIdx] # can be nan
		if math.isnan(stackSegment):
			return None
		else:
			return stackSegment

class testmmMap():
	"""
	docstring for testmmMap
	"""
	def __init__(self):
		pass
