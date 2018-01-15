"""
Get files from a mmserver using REST interface.

Examples::

	from pymapmanager import mmio
	s = mmio.mmio()

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

from __future__ import print_function
import os, time, requests

default_server_url = 'http://localhost:5010/'
default_user = 'public'

default_eol = '\n'

debugThis = False

class mmio():

	####################################################
	## init
	####################################################
	def __init__(self, server_url=default_server_url, username=default_user):
		"""
		Establish connection to a mmserver.
		
		Args:
			server_url (str): The full url to the mmServer
				For example: 'http://localhost:5000/'
			username (str): A valid username.
				For example: 'public'
		"""
		self.server_url = server_url
		self.username = username
		
		if debugThis:
			print('mmio.__init__(): server_url:', server_url)
		url = server_url + 'api/v1/status'
		response = requests.get(url)
		response.raise_for_status()

		if debugThis:
			print('   server responded:', response.content)
		
	####################################################
	## get
	####################################################
	def maplist(self):
		"""
		Get list of maps for user username
		"""
		url = self.server_url + 'api/v1/maplist/' + self.username
		response = requests.get(url)
		if response.status_code == 404:
			print('error: mmio.maplist() received a 404 for url:', url)
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
		
		url = self.server_url + 'api/v1/getfile/' + type + '/' + self.username + '/' + mapname
		if timepoint is not None:
			url += '/' + str(timepoint)
		if channel is not None:
			url += '/' + str(channel)
			
		if debugThis:
			print('mmio.getfile() url:', url)
		response = requests.get(url)
		if response.status_code == 404:
			print('error: mmio.getfile() received a 404 for url:', url)
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
		if debugThis:
			print('mmio.getimage() url:', url)
		response = requests.get(url)
		if response.status_code == 404:
			print('error: mmio.getimage() received a 404 for url:', url)
		return response.content

	####################################################
	## post
	####################################################
	def postmap(self, mapFolder):
		"""
		Post a map to the server.

		Args:
			mapFolder (str) full path to map folder (local machine).
		"""
		startTime = time.time()

		print('mmio.postmap() posting map to server:', self.server_url, 'user:', self.username)

		mapname = os.path.basename(mapFolder)

		# main header file
		mapFile = os.path.join(mapFolder, mapname + '.txt')
		if os.path.isfile(mapFile):
			file = {'file': open(mapFile, 'rb')}
			url = 'post/' + self.username + '/' + mapname + '/header'
			#print('uploading main map file with url:', url)
			r = requests.post(self.server_url + url, files=file)
			#print('   Response:', r.content)

		# obj map
		objMapFile = os.path.join(mapFolder, mapname + '_objMap.txt')
		if os.path.isfile(objMapFile):
			file = {'file': open(objMapFile, 'rb')}
			url = 'post/' + self.username + '/' + mapname + '/header'
			#print('uploading obj map file with url:', url)
			r = requests.post(self.server_url + url, files=file)
			#print('   Response:', r.content)

		# seg map
		segMapFile = os.path.join(mapFolder, mapname + '_segMap.txt')
		if os.path.isfile(segMapFile):
			file = {'file': open(segMapFile, 'rb')}
			url = 'post/' + self.username + '/' + mapname + '/header'
			#print('uploading seg map file with url:', url)
			r = requests.post(self.server_url + url, files=file)
			#print('   Response:', r.content)

		# all stackdb
		stackdbFolder = os.path.join(mapFolder, 'stackdb')
		if os.path.isdir(stackdbFolder):
			for file in os.listdir(stackdbFolder):
				if file.endswith('.txt'):
					stackdbFile = os.path.join(stackdbFolder, file)
					fileid = {'file': open(stackdbFile, 'rb')}
					url = 'post/' + self.username + '/' + mapname + '/stackdb'
					#print('uploading stackdb file:', file, url)
					r = requests.post(self.server_url + url, files=fileid)

		# all lines
		lineFolder = os.path.join(mapFolder, 'line')
		if os.path.isdir(lineFolder):
			for file in os.listdir(lineFolder):
				if file.endswith('.txt'):
					lineFile = os.path.join(lineFolder, file)
					fileid = {'file': open(lineFile, 'rb')}
					url = 'post/' + self.username + '/' + mapname + '/line'
					#print('uploading line file:', file, url)
					r = requests.post(self.server_url + url, files=fileid)

		stopTime = time.time()
		print('Done uploading map:', mapFolder, 'in', round(stopTime-startTime,2), 'seconds.')

if __name__ == '__main__':
	if 0:
		s = mmio()
		map = '../examples/exampleMaps/rr30a/rr30a.txt'
		s.postmap(map)
	if 1:
		io = mmio(username='public')
		maplist = io.maplist()
		print('main: maplist:', maplist)
		
		header = io.getfile('header', 'rr30a')
		for line in header.split('\r'):
			print(line)

		objmap = io.getfile('objmap', 'rr30a')
		print(objmap.split('\r')[0])
		print(objmap.split('\r')[1])

		stackdb = io.getfile('stackdb', 'rr30a', timepoint=0)
		print('stackdb:', stackdb.split('\r')[0])

		line = io.getfile('line', 'rr30a', timepoint=3)
		print('line:', line.split('\r')[0])

		int1 = io.getfile('int', 'rr30a', 0, channel=1)
		print('int1:', int1.split('\r')[0])

		int2 = io.getfile('int', 'rr30a', timepoint=2, channel=2)
		print('int2:', int2.split('\r')[0])

		image = io.getimage('rr30a', timepoint=1, slice=5, channel=2)
		#print 'image:', image
