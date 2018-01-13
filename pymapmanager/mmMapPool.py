import os, time
from glob import glob # for pool

from pymapmanager.mmMap import mmMap

class mmMapPool():
	"""
	Load all maps in a folder.

	Args:
		path (str): Full path to a folder containing folders of maps.

	Example::

		folderPath = myMapFile = 'PyMapManager/examples/exampleMaps/'
		maps = mmMapPool(folderPath)
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
		List of :class:`pymapmanager.mmMap` in the mmMapPool.
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
