"""

"""

import requests

default_server_url = 'http://127.0.0.1:5000/'
default_user = 'cudmore'

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
		response = requests.get(server_url)
		response.raise_for_status()

	def maplist(self):
		"""
		Return list of maps for user username
		"""
		url = self.server_url + self.username + '/maps'
		response = requests.get(url)
		#print response.content

	def getfile(self, type, mapname, timepoint=None, channel=None):
		"""
		Get a file from a map.
		
		Args:
			type (str): One of (header, objmap, segmap, stackdb, line, int)
			mapname (str):
			timepoint (int):
			channel (int): Required for type=int
			
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
		
if __name__ == '__main__':
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
