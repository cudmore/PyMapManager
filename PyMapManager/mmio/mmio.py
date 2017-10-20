"""
Use this to load (get) files from a mmserver.
This is a temporary wrapper as mmserver is currently a Flask server (slow).
Eventually transition this to use proper online repository like ndio.

To Do: add Rest interface to get number of timepoints in a map?

Examples::

	from pymapmanager.mmio import mmio
	s = mmio.mmio()
		Success, the server at http://robertcudmore.org/mmserver/ is up and running!

	s.maplist()
		["rr30a", "rr58c"]
	
	# these are the basic files that we can get for map 'rr30a'
	# they will each return text that can be converted to a stringio and read into python (numpy and/or panda)
	s.getfile('header', 'rr30a')
	s.getfile('objmap', 'rr30a')
	s.getfile('segmap', 'rr30a')
	s.getfile('stackdb', 'rr30a', timepoint=0)
	s.getfile('line', 'rr30a', timepoint=0)
	s.getfile('int', 'rr30a', timepoint=0, channel=1)
	
	# a bad request looks like this
	s.getfile('header', 'bad map')
		error: mmio.getfile() received a 404 for url: http://robertcudmore.org/mmserver/public/bad map/header

	# upload a map
	map = '/Users/cudmore/MapManagerData/richard/Nancy/rr30a'
	s.postmap(map)

Notes::
	Header files are saved with \n
	Stackdb, int, and line files are saved with \r

"""

import os, requests

#default_server_url = 'http://127.0.0.1:5000/'
default_server_url = 'http://robertcudmore.org/mmserver/'
default_server_url = 'http://cudmore.duckdns.org:5010/'
default_user = 'public'

default_eol = '\n'

class mmio():

	def __init__(self, server_url=default_server_url, username=default_user):
		"""
		Establish connection to a mmserver.
		
		Args:
			server_url (str): The full url to the mmServer
				For example: http://127.0.0.1:5000/
			username (str): A valid username.
				For example: cudmore
		"""
		self.server_url = server_url
		self.username = username
		
		# check if url responded correctly
		print 'server_url:', server_url
		response = requests.get(server_url)
		response.raise_for_status()

		print 'server responded:', response.content
		#print 'Success, the server at', server_url, 'is up and running!'
		
	def maplist(self):
		"""
		Return list of maps for user username
		"""
		url = self.server_url + self.username + '/maps'
		response = requests.get(url)
		if response.status_code == 404:
			print 'error: mmio.maplist() received a 404 for url:', url
		return response.content
		
	def getfile(self, type, mapname, timepoint=None, channel=None):
		"""
		Get a file from a map.
		
		Args:
			type (str): One of (header, objmap, segmap, stackdb, line, int)
			mapname (str):
			timepoint (int):
			channel (int): Required for type=int
			
		To Do::
			Server should mirror mmMap and mmStack. For example, merge stackdb and int

		"""
		baseurl = self.server_url + self.username + '/' + mapname + '/'
		if type == 'header':
			url = baseurl + 'header'
		elif type == 'objmap':
			url = baseurl + 'objmap'
		elif type == 'segmap':
			url = baseurl + 'segmap'		
		elif type == 'stackdb':
			url = baseurl + str(timepoint) + '/stackdb'
		elif type == 'line':
			url = baseurl + str(timepoint) + '/line'
		elif type == 'int':
			url = baseurl + str(timepoint) + '/int/' + str(channel)
		else:
			# error
			url = ''
		# print 'url:', url
		response = requests.get(url)
		if response.status_code == 404:
			print 'error: mmio.getfile() received a 404 for url:', url
		return response.content
			
	def getimage(self, mapname, timepoint, slice, channel=1):
		"""
		Get an image from a map.
		
		Args:
			mapname (str):
			timepoint (int):
			slice (int):
			channel (int):
			
		Note::
			For now this is the whole 3D stack, need to make it one slice.
		"""
		
		url = self.server_url + self.username + '/' + mapname + '/' + str(timepoint) \
			+ '/image/' + str(slice) + '/' + str(channel)
		response = requests.get(url)
		if response.status_code == 404:
			print 'error: mmio.getimage() received a 404 for url:', url
		return response.content

	def postmap(self, mapFolder):
		"""
		Post a map to the server.

		Args:
			mapFolder (str) full path to map folder (local machine).
		"""
		print 'posting map to server:', self.server_url, 'user:', self.username

		mapname = os.path.basename(mapFolder)

		# main header file
		mapFile = os.path.join(mapFolder, mapname + '.txt')
		if os.path.isfile(mapFile):
			file = {'file': open(mapFile, 'rb')}
			url = 'post/' + self.username + '/' + mapname + '/header'
			print 'uploading main map file with url:', url
			r = requests.post(default_server_url + url, files=file)
			print '   Response:', r.content

		# obj map
		objMapFile = os.path.join(mapFolder, mapname + '_objMap.txt')
		if os.path.isfile(objMapFile):
			file = {'file': open(objMapFile, 'rb')}
			url = 'post/' + self.username + '/' + mapname + '/header'
			print 'uploading obj map file with url:', url
			r = requests.post(default_server_url + url, files=file)
			print '   Response:', r.content

		# seg map
		segMapFile = os.path.join(mapFolder, mapname + '_segMap.txt')
		if os.path.isfile(segMapFile):
			file = {'file': open(segMapFile, 'rb')}
			url = 'post/' + self.username + '/' + mapname + '/header'
			print 'uploading seg map file with url:', url
			r = requests.post(default_server_url + url, files=file)
			print '   Response:', r.content

		# all stackdb
		stackdbFolder = os.path.join(mapFolder, 'stackdb')
		if os.path.isdir(stackdbFolder):
			for file in os.listdir(stackdbFolder):
				if file.endswith('.txt'):
					stackdbFile = os.path.join(stackdbFolder, file)
					fileid = {'file': open(stackdbFile, 'rb')}
					url = 'post/' + self.username + '/' + mapname + '/stackdb'
					print 'uploading stackdb file:', file, url
					r = requests.post(default_server_url + url, files=fileid)

		# all lines
		lineFolder = os.path.join(mapFolder, 'line')
		if os.path.isdir(lineFolder):
			for file in os.listdir(lineFolder):
				if file.endswith('.txt'):
					lineFile = os.path.join(lineFolder, file)
					fileid = {'file': open(lineFile, 'rb')}
					url = 'post/' + self.username + '/' + mapname + '/line'
					print 'uploading line file:', file, url
					r = requests.post(default_server_url + url, files=fileid)

		print 'Done uploading map:', mapFolder

if __name__ == '__main__':
	if 1:
		s = mmio()
		map = '/Users/cudmore/MapManagerData/richard/Nancy/rr58c'
		s.postmap(map)
	if 0:
		io = mmio(username='cudmore')
		io.maplist()

		header = io.getfile('header', 'rr30a')
		for line in header.split('\r'):
			print line

		objmap = io.getfile('objmap', 'rr30a')
		print objmap.split('\r')[0]
		print objmap.split('\r')[1]

		stackdb = io.getfile('stackdb', 'rr30a', timepoint=0)
		print 'stackdb:', stackdb.split('\r')[0]

		line = io.getfile('line', 'rr30a', timepoint=3)
		print 'line:', line.split('\r')[0]

		int1 = io.getfile('int', 'rr30a', 0, channel=1)
		print 'int1:', int1.split('\r')[0]

		int2 = io.getfile('int', 'rr30a', timepoint=2, channel=2)
		print 'int2:', int2.split('\r')[0]

		image = io.getimage('rr30a', timepoint=1, slice=5, channel=2)
		#print 'image:', image
