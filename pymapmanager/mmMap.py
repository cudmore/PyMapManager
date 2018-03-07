from __future__ import print_function

import os, io, time, math
from errno import ENOENT
import pandas as pandas
import numpy as np
#import tifffile

import scipy.misc

#from pymapmanager.version import __version__

from pymapmanager.mmUtil import newplotdict
from pymapmanager.mmStack import mmStack
from pymapmanager.mmio import mmio

'''3D numpy array, rows are stack centric indices, columns are sessions, 3rd dimension is:
	[0] idx, [1] next, [2] nextTP, [3] prev, [4] prevTP
	[5] blank, [6] runIdx, [7] dynType, [8] forced
	[9] nodeType, [10] segmentID, [11] splitIdx
'''

class mmMap():
	"""
	A time-series of :class:`pymapmanager.mmStack` time-points plus some book-keeping to link corresponding annotations
	and segments between time-points.

	Args:
		filePath (str):
			Either: Full path to map folder.
			Or: Full file path to .txt file for the map. File is inside map folder, for map a5n it is '/a5n/a5n.txt'.
		urlmap (str): Name of the map to load from a :class:`pymapmanager.mmio` online repository.

	Example::

		from pymapmanager import mmMap
		myMapPath = 'PyMapManager/examples/exampleMaps/rr30a'
		myMap = mmMap(filePath=myMapPath)

		# Get the 3rd mmStack using
		stack = myMap.stacks[3]

		# Retrieve annotations (for a given segmentID) across all time-points in the map
		pDist_values = myMap.getMapValues2('pDist', segmentID=[3])
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

		# removed 20170107, replaced with xxx
		# self.defaultRoiType = 'spineROI'
		#self.defaultRoiTypeID = 0
		
		self.server = None
		# Pointer to :class:`pymapmanager.mmio` server connection.
		# Only used to load from urlmap.

		self.objMap = None
		# 2D array where each row is a run of annotations.
		# objMap[i][j] gives us a mmStack centric index into mmStack.stackdb.

		self.segMap = None
		# 2D array where each row is a run of segments.
		# segMap[i][j] gives us mmStack centric index into mmStack._line
		
		self.segRunMap = None # 20180107, why was this not defaulted?
		
		# if we get a filePath, make sure it exists and decide if it is a folder or a file
		# in the end we will always load from a .txt file
		if filePath is not None:
			if filePath.endswith(os.sep):
				filePath = filePath[0:-1]
			if os.path.exists(filePath):
				if os.path.isdir(filePath):
					tmpPath, tmpName = os.path.split(filePath)
					filePath = os.path.join(filePath, tmpName + '.txt')
					# check if file exists
					if not os.path.isfile(filePath):
						raise IOError(ENOENT, 'mmMap got a bad map folder:', filePath)
				else:
					pass
			else:
				# error
				raise IOError(ENOENT, 'mmMap got a bad map path:', filePath)
		
		###############################################################################
		# map nv
		doFile = True
		if filePath is not None:
			if not os.path.isfile(filePath):
				raise IOError(ENOENT, 'mmMap did not find filePath:', filePath)
			self.filePath = filePath #  Path to file used to open map."""
			self._folder = os.path.dirname(filePath) + '/'
			self.name = os.path.basename(filePath).strip('.txt')
			self.table = pandas.read_table(filePath, index_col=0)
		elif urlmap is not None:
			doFile = False
			# try loading from url
			self.name = urlmap
			self.server = mmio()
			tmp = self.server.getfile('header', self.name)
			self.table = pandas.read_table(io.StringIO(tmp.decode('utf-8')), index_col=0)

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
		self.runMap = self._buildRunMap(self.objMap, roiTypeID=self.defaultAnnotationID)

		###############################################################################
		# segMap (3d)
		header = None
		if doFile:
			segMapFile = self._folder + self.name + '_segMap.txt'
			if os.path.isfile(segMapFile):
				with open(segMapFile, 'rU') as f:
					header = f.readline().rstrip()
				self.segMap = np.loadtxt(segMapFile, skiprows=1)
			else:
				#raise IOError(ENOENT, 'mmMap did not find segMapFile:', segMapFile)
				print('did not find segment map file, should be ok')
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
			self.segRunMap = self._buildRunMap(self.segMap, roiTypeID = None)

		###############################################################################
		#load each stack db
		# this assumes self.objMap has already been loaded
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
		print('map', self.name, 'loaded in', round(stopTime-startTime,2), 'seconds.')

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
		if self.segMap is not None:
			numSegments = self.segRunMap.shape[0]
		else:
			numSegments = 0
		return numSegments

	@property
	def defaultAnnotation(self):
		"""
		"""
		
		# if defaultAnnotation does not exist then default to 'spineROI'
		if 'defaultAnnotation' in self.table.index:
			theRet = self.table.loc['defaultAnnotation'][0]
			# if empty then we assume 'spineROI'
			if theRet == '':
				theRet = 'spineROI'
		else:
			theRet = 'spineROI'
		return theRet

	@property
	def defaultAnnotationID(self):
		theRet = 0
		defaultAnnotation = self.defaultAnnotation
		if defaultAnnotation == 'spineROI':
			theRet = 0
		elif defaultAnnotation == 'otherROI':
			theRet = 4
		return theRet

	def __str__(self):
		objCount = 0
		for stack in self.stacks:
			objCount += stack.numObj
		'''
		theRet = {}
		theRet['info'] = ('map:' + self.name
			+ ' map segments:' + str(self.numMapSegments)
			+ ' stacks:' + str(self.numSessions)
			+ ' total object:' + str(objCount))
		theRet['map'] = self
		'''
		retStr = ('map:' + self.name
			+ ' map segments:' + str(self.numMapSegments)
			+ ' stacks:' + str(self.numSessions)
			+ ' total object:' + str(objCount))
		return retStr

	def __iter__(self):
		i = 0
		while i < len(self.stacks):
			yield self.stacks[i]
			i += 1

	def mapInfo(self):
		"""
		Get information on the map
		
		Returns:
			| A dict of
			| mapName : Str
			| numSessions : Int
			| numChannels : Int
			| numMapSegments : Int
			| 
			| The following are string list with numSessions elements
			| stackNames : 
			| importedStackName : 
			| numSlices : 
			| date : 
			| time : 
			| dx : Voxel size in um
			| dy : Voxel size in um
			| dz : Voxel size in um
			| px : Number of Pixels
			| py : Number of Pixels
			| pz : Number of Pixels
			| ...
		"""
		theRet = {}
		theRet['mapName'] = self.name
		theRet['numSessions'] = self.numSessions
		theRet['numChannels'] = self.numChannels
		theRet['defaultAnnotation'] = self.defaultAnnotation
		theRet['numAnnotations'] = 0
		# lists, one value per session
		theRet['stackNames'] = []
		theRet['importedStackName'] = []
		theRet['date'] = []
		theRet['time'] = []
		theRet['px'] = [] # pixels
		theRet['py'] = []
		theRet['numSlices'] = []
		theRet['dx'] = [] # voxels in um
		theRet['dy'] = []
		theRet['dz'] = []
		theRet['numROI'] = []
		for idx in range(self.numSessions):
			theRet['stackNames'].append(self.table.loc['hsStack'][idx])
			theRet['importedStackName'].append(self.table.loc['importedStackName'][idx])
			theRet['date'].append(self.table.loc['date'][idx])
			theRet['time'].append(self.table.loc['time'][idx])
			theRet['px'].append(self.table.loc['px'][idx])
			theRet['py'].append(self.table.loc['py'][idx])
			theRet['numSlices'].append(self.table.loc['pz'][idx]) # changing name

			theRet['dx'].append(self.table.loc['dx'][idx])
			theRet['dy'].append(self.table.loc['dy'][idx])
			theRet['dz'].append(self.table.loc['dz'][idx])
			
			thisNum = self.stacks[idx].countObj(roiType=self.defaultAnnotation)
			theRet['numROI'].append(thisNum)
			theRet['numAnnotations'] = theRet['numAnnotations'] + self.stacks[idx].numObj
			
			runIdx = 6

		if self.segMap is not None:
			theRet['numMapSegments'] = self.segRunMap.shape[0]
		else:
			theRet['numMapSegments'] = 0

		'''
		# these were not being used
		theRet['objMap'] = self.objMap[runIdx].astype('int') # from spine index to run index
		theRet['runMap'] = self.runMap.astype('int') # from run idx to spine idx
		theRet['segMap'] = None
		theRet['numMapSegments'] = 0
		if self.segMap is not None:
			theRet['segMap'] = self.segMap.astype('int')
			theRet['numMapSegments'] = self.segRunMap.shape[0]
		'''
					
		#print 'mapInfo() theRet:', theRet
		return theRet

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

	def getMapDynamics(self, pd, thisMatrix=None):
	
		if thisMatrix is None:
			pd = self.getMapValues3(pd)
			thisMatrix = pd['stackidx']
		
		m = thisMatrix.shape[0]
		n = thisMatrix.shape[1]
			
		pd['dynamics'] = np.empty([m,n])
		pd['dynamics'][:] = np.NAN
		
		# 1:add, 2:sub, 3:transient, 4:persisten
		kAdd = 1
		kSubtract = 2
		kTransient = 3
		kPersistent = 4
		
		for i in range(m):
			for j in range(n):
				if not thisMatrix[i,j]>=0:
					continue
				if j==0:
					if thisMatrix[i,j+1]>=0:
						pd['dynamics'][i,j] = kPersistent
					else:
						pd['dynamics'][i,j] = kSubtract
				elif j==n-1:
					if thisMatrix[i,j-1]>=0:
						pd['dynamics'][i,j] = kPersistent
					else:
						pd['dynamics'][i,j] = kAdd
				else:
					added = not thisMatrix[i,j-1]>=0
					subtracted = not thisMatrix[i,j+1]>=0
					if added and subtracted:
						pd['dynamics'][i,j] = kTransient
					elif added:
						pd['dynamics'][i,j] = kAdd
					elif subtracted:
						pd['dynamics'][i,j] = kSubtract
					else:
						pd['dynamics'][i,j] = kPersistent
				
		return pd
		
	def ingest(self, tp, channel=1):
		"""
		Take a raw 3D .tif and populate raw/ingest/tp<tp> with single channel .tif files.

		Args:
		    tp (int) : The timepoint to ingest
		    channel (int) : The channel to ingest, valid channels are (1,2,3)

		Returns:
		    None
		"""

		print('mmMap.ingest() is ingesting tp:', tp, 'channel:', channel)

		outFileType = '.png'

		# '/Users/cudmore/Desktop/tmp/'
		savePath = self._folder # ends in '/'
		savePath += 'raw/'
		if not os.path.isdir(savePath):
			os.makedirs(savePath)
		savePath += 'ingested/'
		if not os.path.isdir(savePath):
			os.makedirs(savePath)
		savePath += 'tp' + str(tp) + '/'
		if not os.path.isdir(savePath):
			os.makedirs(savePath)

		maxSavePath = self._folder + 'raw/ingested/'

		print('   loading full 3d .tif')
		# load the full 3D .tif
		image = self.stacks[tp].loadStackImages(channel=channel)
		print('   image shape:', image.shape)
		[slices, m, n] = image.shape
		for slice in range(slices):
			outfile = self.name + '_tp' + str(tp) + '_ch' + str(channel) + '_s' + str(slice).zfill(4) + outFileType
			outfilepath = savePath + outfile

			if slice % 10 == 0:
				print('   saving slice:', slice, 'of', slices, outfilepath)

			# this saves .png as 8-bit, I am not sure if it is doing normalization?
			scipy.misc.imsave(outfilepath, image[slice,:,:])

		# make maximal intensity projection
		maxfile = 'MAX_' + self.name + '_tp' + str(tp) + '_ch' + str(channel) + outFileType
		maxfilepath = maxSavePath + maxfile
		print('   making and saving max project', maxfilepath)
		max_ = np.zeros((m, n), dtype='uint8')
		for slice in range(slices):
			max_ = np.maximum(max_, image[slice,:,:])
		# MAX_rr30a_tp0_ch2
		scipy.misc.imsave(maxfilepath, max_)

		print('done ingesting')

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
		
		# always make a matrix of bad
		isBad = np.empty([m, n])
		isBad[:] = np.NAN

		# keep track of map segment id
		yMapSegment = []
		if self.segMap is not None:
			yMapSegment = np.empty([m, n])
			yMapSegment[:] = np.NAN

		# 20171225, cPnt is overkill but until I rewrite REST
		# to get list of stat (x,y,z,pDist, cPnt, cx, cy, cz) etc. etc.
		cPnt = np.empty([m, n])
		cPnt[:] = np.NAN
		
		runIdxDim = 6

		if pd['stacklist'] is not None and len(pd['stacklist'])>0:
			myRange = pd['stacklist']
		else:
			myRange = range(n)

		for j in myRange:

			#print('*** getMapValues3() j:', j, "pd['segmentid']:", pd['segmentid'])
			orig_df = self.stacks[j].stackdb

			currSegmentID = []
			if self.numMapSegments > 0:
				if pd['segmentid'] is not None and pd['segmentid'] >=0 :
					currSegmentID = self.segRunMap[pd['segmentid'], j]  # this only works for one segment -- NOT A LIST
					#print('   currSegmentID:', currSegmentID)
					if currSegmentID >= 0:
						currSegmentID = int(currSegmentID)
						# print 'getMapValues3() j:', j, 'currSegmentID:', currSegmentID
						currSegmentID = [currSegmentID]
					else:
						currSegmentID = []
				#print('   currSegmentID:', currSegmentID)
				if pd['segmentid'] is not None and pd['segmentid'] >= 0 and not currSegmentID:
					# this session does not have segmentID that match
					#print('   getMapValues3() skipping tp', j)
					continue

			goodIdx = self.runMap[:, j]  # valid indices from runMap

			#print goodIdx
			
			runMap_idx = orig_df.index.isin(goodIdx)  # series of boolean (Seems to play nice with nparray)

			if pd['roitype']:
				roiType_idx = orig_df['roiType'].isin(pd['roitype'])
				runMap_idx = runMap_idx & roiType_idx
			if currSegmentID:
				segmentID_idx = orig_df['parentID'].isin(currSegmentID)
				runMap_idx = runMap_idx & segmentID_idx
			
			# bad
			if not pd['plotbad']:
				#print('mmMap.getMapValues3() is stripping out isBad')
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
			except (KeyError, e):
				print('getMapValues3() KeyError - reason ', str(e))
			except:
				print('getMapValues3() error in assignment')

			# keep track of stack centric spine idx
			yIdx[finalRows, j] = final_df.index.values
			ySess[finalRows, j] = j
			yRunRow[finalRows, j] = finalRows  # final_df.index
			
			# bad
			if pd['plotbad']:
				bad_idx = final_df['isBad'].isin([1])
				'''
				if j == 3:
					print(j, 'finalRows.shape:', finalRows.shape, finalRows.dtype)
					print(j, 'bad_idx.shape:', bad_idx.shape, bad_idx.dtype)
					print(final_df[['Idx', 'isBad']])
				'''
				isBad[finalRows, j] = bad_idx

			#print 'a', final_df['parentID'].values.astype(int)
			#print 'b', self.segMap[0, final_df['parentID'].values.astype(int), j]
			if self.segMap is not None:
				yMapSegment[finalRows, j] = self.segMap[0, final_df['parentID'].values.astype(int), j]

			cPnt[finalRows, j] = final_df['cPnt'].values
			
			if pd['xstat'] == 'session':
				#print 'swapping x for session'
				pd['x'][finalRows, j] = j #ySess[finalRows,j]

		# strip out all nan rows, can't do this until we have gone through all sessions
		# makes plotting way faster
		ySess = ySess[~np.isnan(yIdx).all(axis=1)]
		yRunRow = yRunRow[~np.isnan(yIdx).all(axis=1)]
		if pd['plotbad']:
			isBad = isBad[~np.isnan(yIdx).all(axis=1)]
		if self.segMap is not None:
			yMapSegment = yMapSegment[~np.isnan(yIdx).all(axis=1)] # added 20171220
		cPnt = cPnt[~np.isnan(yIdx).all(axis=1)] # added 20171225
		if pd['xstat']:
			pd['x'] = pd['x'][~np.isnan(yIdx).all(axis=1)]
		if pd['ystat']:
			pd['y'] = pd['y'][~np.isnan(yIdx).all(axis=1)]
		if pd['zstat']:
			pd['z'] = pd['z'][~np.isnan(yIdx).all(axis=1)]
		yIdx = yIdx[~np.isnan(yIdx).all(axis=1)] # do this last


		pd['stackidx'] = yIdx
		pd['mapsess'] = ySess
		pd['runrow'] = yRunRow
		pd['mapsegment'] = yMapSegment
		pd['cPnt'] = cPnt
		if pd['plotbad']:
			pd['isBad'] = isBad
		else:
			pd['isBad'] = None

		if pd['getMapDynamics']:
			# creates pd['dynamics']
			pd = self.getMapDynamics(pd, thisMatrix=pd['stackidx'])
		
		stopTime = time.time()
		print('mmMap.getMapValues3() took', round(stopTime - startTime, 2), 'seconds')

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

	def _buildRunMap(self, theMap, roiTypeID=None):
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
		nodeType = 9 # integer encoding type, spineROI==0
		m = theMap.shape[1]
		n = theMap.shape[2]
		k = theMap.shape[0]

		# reset 
		theMap[runIdx][:][:] = '-1'
		
		# 20171222
		# was this
		#numRows = np.count_nonzero(~np.isnan(theMap[idx,:,0]))
		#retRunMap = np.empty([numRows,n]) #, dtype=int)
		# new
		retRunMap = np.empty([1, n])  #, dtype=int) # start as one row in run map
		retRunMap[:] = 'nan'

		emptyRow = np.empty([1, n])
		emptyRow[:] = 'nan'

		# thisroitype = 'spineROI'
		
		currRow = 0
		for j in range(0,n): #sessions
			# not loaded yet
			#stackdb = self.stacks[j].stackdb
			if j == 0:
				firstSessionAdded = 0
			for i in range(0,m):
				#retRunMap[i,j] = 'nan'
				# 20171221, if i just break on ! roiType (e.g. spine) then we get a run map without nan rows?
				# we need to add an updated %runIdx as we do this, e.g. theMap[runIdx][i][j]= currRow
				# new
				#if theMap[idx,i,j]>=0 and stackdb[i][%roiType] == thisroitype:
				#	pass
				#else:
				#	break
				# was this
				# if theMap[idx,i,j]>=0:
				if theMap[idx,i,j]>=0 and (roiTypeID is None or theMap[nodeType][i][j] == roiTypeID):
					pass
				else:
					continue
				if j==0:
					'''
					# was this 20171222
					currRow = i
					#currRow = firstSessionAdded
					# new one line 20171222
					# retRunMap = np.vstack([retRunMap, emptyRow])
					retRunMap[currRow, j] = i
					# new
					#theMap[runIdx,i,j] = currRow
					'''

					if firstSessionAdded == 0:
						currRow = 0
						firstSessionAdded += 1
					else:
						retRunMap = np.vstack([retRunMap, emptyRow])
						currRow += 1
					retRunMap[currRow, j] = i
					# new
					theMap[runIdx,i,j] = currRow
				elif not (theMap[prev,i,j]>=0):
					currRow += 1
					retRunMap = np.vstack([retRunMap, emptyRow])
					retRunMap[currRow, j] = i
					# new
					theMap[runIdx,i,j] = currRow
				else:
					continue
				#retRunMap[currRow,j] = i
				nextNode = theMap[next,i, j]
				for k in range(j+1,n):
					if nextNode >= 0:
						retRunMap[currRow,k] = nextNode
						# new, double check this
						theMap[runIdx,int(nextNode),k] = currRow
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

if __name__ == '__main__':
	path = '../examples/exampleMaps/THet2a/THet2a.txt'
	path = '../examples/exampleMaps/BD_NGDG450/BD_NGDG450.txt'
	path = '../examples/exampleMaps/rr30a/rr30a.txt'

	print('path:', path)
	m = mmMap(path)

	print(m)
	print('m.runMap.shape : ', m.runMap.shape)
	for idx, stack in enumerate(m.stacks):
		print('tp:', idx, 'n:', stack.stackdb.shape)

	from pymapmanager.mmUtil import newplotdict

	plotDict = newplotdict()
	plotDict['plotbad'] = True
	plotDict['roitype'] = m.defaultAnnotation
	plotDict['xstat'] = 'days'
	plotDict['ystat'] = 'pDist'
	plotDict['zstat'] = 'ubssSum_int2'  # 'sLen3d_int1' #swap in any stat you like, e.g. 'ubssSum_int2'
	plotDict['segmentid'] = 1 #[0]
	plotDict['getMapDynamics'] = True

	plotDict = m.getMapValues3(plotDict)

	print("\nplotDict['x'].shape : ", plotDict['x'].shape)

	# test is bad
	#print("plotDict['stackidx']:", plotDict['stackidx'].shape, plotDict['stackidx'].dtype)
	#print("plotDict['isBad']:", plotDict['isBad'].shape, plotDict['isBad'].dtype)
	#plotDict['isBad'])
	#for row in plotDict['isBad']:
	#	print(row)
		
	# test line
	# THet2a has a stack but NO tracing and NO spines at session 0
	if 0:
		session = 0
		plotDict = m.stacks[session].line.getLineValues3(plotDict)
		if plotDict['x']:
			print("line plotDict['x'].shape:", plotDict['x'].shape)
			print("line plotDict['sDist'].shape:", plotDict['sDist'].shape)
		else:
			print('__main__ did not find a line at session:', session)
			
	if 0:
		print('\nm.mapInfo():')
		mapInfo = m.mapInfo()
		for key, value in mapInfo.iteritems():
			print(key, value)
		
	#from flask import jsonify
	#print jsonify(mapInfo)
	
	#import json
	#print json.dumps(mapInfo)
	
	
	# dynamics
	#plotDict = m.getMapDynamics(plotDict)
	#print plotDict['dynamics']
	