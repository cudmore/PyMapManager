from __future__ import print_function

import os, io, math
from errno import ENOENT
import pandas as pd
import numpy as np

class mmStackLine():
	"""
	A stack line represents a 3D tracing of a number of dendritic segments.

	Each spineROI annotation in a mmStack is associated with one segmentID.

	Example::

		from pymapmanager.mmMap import mmMap
		myMapFile = 'PyMapManager/examples/exampleMaps/rr30a/rr30a.txt'
		myMap = mmMap(filePath=myMapFile)

		# Get the (x,y,z) values, in um, of the 2nd mmStack tracing
		xyz = myMap.stacks[2].getLine()
	"""
	def __init__(self,stack):
		"""
		Load a line tracing for a stack. In addition to (x,y,z), the line has 'parentID' to specify multiple dendritic tracings

		Args:
			stack (:class:`pymapmanager.mmStack`): The stack that will own the line.

		"""
		self.stack = stack
		"""
		The parent stack
		"""
		self.linedb = None
		"""
		Pandas dataframe of line with (x,y,z,ID) columns.
		"""

		header = None
		if stack.urlmap is not None:
			# careful, we use tmp later to load (we need to know # header rows)
			tmp = self.stack.server.getfile('line', stack.urlmap, timepoint=stack.mapSession)
			header = tmp.split('\r')[0]
		else:
			if stack.map_:
				lineFile = stack._folder + 'line' + '/' + stack.name + '_l.txt'
			else:
				lineFile = stack._folder + 'stackdb' + '/' + stack.name + '_l.txt'
			#if not os.path.isfile(lineFile):
			#	raise IOError(ENOENT, 'mmStackLine did not find lineFile:', lineFile)
			if os.path.isfile(lineFile):
				with open(lineFile, 'rU') as f:
					header = f.readline().rstrip()

		if header is not None:
			if header.endswith(';'):
				header = header[:-1]
			header = header.split(';')
			d = dict(s.split('=') for s in header)

			# line file has a header of segments
			# 1 file header + 1 segment header + numHeaderRow
			numHeaderRow = int(d['numHeaderRow'])
			startReadingRow = 1 + 1 + numHeaderRow

			if stack.urlmap is not None:
				self.linedb = pd.read_csv(io.StringIO(tmp.decode('utf-8')), header=startReadingRow, index_col=False)
			else:
				self.linedb = pd.read_csv(lineFile, header=startReadingRow, index_col=False)

	def getLineValues3(self,pd):
		"""
		Args:
			pd (dict): See mmUtil.newplotdict()

		Returns: pd with ['x'], ['y'], and ['z'] values filled in as numpy ndarray
		"""

		pd['x'] = None
		pd['y'] = None
		pd['z'] = None
		# 20171222 adding sDist and ID for web client
		pd['sDist'] = None
		pd['ID'] = None

		if self.linedb is None:
			print('warning: getLineValues3() did not find a line')
		else:
			df = self.linedb
			if pd['segmentid'] is not None and pd['segmentid'] >= 0:
				# we are passing pd['segmentid'] as an int
				df = df[df['ID'].isin([pd['segmentid']])]
			pd['x'] = df['x'].values
			pd['y'] = df['y'].values
			pd['z'] = df['z'].values
			# 20171222 adding sDist and ID for web client
			pd['sDist'] = df['sDist'].values
			pd['ID'] = df['ID'].values
		
		return pd

	def getLine(self,segmentID=[]):
		"""
		Get the x/y/z values of a line tracing. Pass segmentID to get just one tracing. Note, x/y are in um, z is in slices!

		Args:
			segmentID (list): List of int specifying which segmentID, pass [] to get all.

		Return:
			numpy ndarray of (x,y,z)
		"""
		if self.linedb is None:
			return None

		df = self.linedb
		if segmentID:
			df = df[df['ID'].isin(segmentID)]
		ret = df[['x','y','z']].values
		return ret

	def _EuclideanDist(self, from_xyz, to_xyz):
		"""
		Get the euclidean distance between two points, pass tuple[2]=np.nan to get 2d distance

		Args:
			from_xyz (3 tuple):
			to_xyz (3 tuple):

		Returns: float

		"""
		if from_xyz[2] and to_xyz[2]:
			ret = math.sqrt(math.pow(abs(from_xyz[0]-to_xyz[0]),2) \
				+ math.pow(abs(from_xyz[1]-to_xyz[1]),2) \
				+ math.pow(abs(from_xyz[2]-to_xyz[2]),2))
		else:
			ret = math.sqrt(math.pow(abs(from_xyz[0]-to_xyz[0]),2) \
				+ math.pow(abs(from_xyz[1]-to_xyz[1]),2))
		return ret

	def getLineLength(self, segmentID, smoothz=None):
		"""Get the 3D line length for one segment (um)

		Args:
			segmentID (int): Stack centric segmentID, different from other functions, requires an int (not a list)
			smoothz (int): Smooth Z

		Returns:
			3D length (float) of segmentID
		"""
		# strip down df
		df = self.linedb
		df = df[df['ID'].isin(segmentID)]
		# grab x/y/z values (z is in slices!!!)
		values = df[['x', 'y', 'z']].values
		# convert z to microns
		values[:,2] *= self.stack.voxelz # slices * um/slice -->> um
		# filter z
		if smoothz:
			pass
		# step through rows and get euclidean distance between each row i and row i-1
		dist = 0.0
		prev_xyz = (np.nan, np.nan, np.nan)
		for i, row in enumerate(values):
			this_xyz = (row[0], row[1], row[2])
			if i>0:
				dist += self._EuclideanDist(prev_xyz, this_xyz)
			prev_xyz = tuple(this_xyz)
		return dist