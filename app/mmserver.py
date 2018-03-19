"""
Author: Robert Cudmore
Date: 20170808

A http server to serve mmMap files and images.
Server is run using Flask.
Implements a RESTful API.

PyMapManager.mmio is a thin wrapper to provide easy programming interface to the REST api

todo:
	there should be two main routes here: api and data
	- api: is for javascript to get json data
	- data: is for python to get files
	
	- add another playground route to plot directly off server	
"""

from __future__ import print_function
import os, sys
import json
from datetime import datetime

try:
	from cStringIO import StringIO # python 2.x
except ImportError:
	from io import BytesIO as StringIO # python 3.x

from flask import Flask, render_template, send_file, send_from_directory, safe_join
from flask import jsonify, request, make_response
from flask_cors import CORS

from werkzeug import secure_filename, FileStorage

import pandas as pandas
import numpy as np
from skimage.io import imsave, imread
import redis
import pickle

#import pymapmanager
#print('   mmserver: pymapmanager.__version__:', pymapmanager.__version__)

from pymapmanager import mmMap, mmUtil

# local debugging
debugThis = False

# turn off printing to console
if 0:
	import logging
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)

############################################################
# PyMapManager-Data
############################################################

# assuming PyMapManager-Data folder is in same folder as PyMapManager (they are in parallel)
UPLOAD_FOLDER = '../PyMapManager-Data/upload'
data_folder = '../PyMapManager-Data' # docker version

if __name__ == '__main__':
	# debug version
	data_folder = '../../PyMapManager-Data'
else:
	# docker version
	data_folder = '../PyMapManager-Data'
		
############################################################
# app
############################################################
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # upload to server should be proper scp, then flask app can trigger mmMap.ingest
app.config['data_folder'] = data_folder

############################################################
# redis
############################################################
if __name__ == '__main__':
	# debug version
	db = redis.StrictRedis(host='localhost', port=6379, db=0) #connect to redis server
else:
	# docker version
	db = redis.StrictRedis(host='redis', port=6379, db=0) #connect to redis server

############################################################
# routes
############################################################
@app.errorhandler(404)
def not_found(error):
	theRet = {
		'name': 'mmserver',
		'error': 'Not found'
	}
	return make_response(jsonify(theRet), 404)
	
@app.route('/')
def hello_world():
	print('hello_world()')
	index_path = os.path.join(app.static_folder, 'index.html')
	return send_file(index_path)
	#return render_template('index.html')
	#return 'mmserver rest interface. use /help to get started'

# So debug version 'python mmserver' and docker version with nginx can co-exist
# Everything not declared before (not a Flask route / API endpoint)...
@app.route('/images/<path:path>')
def route_frontend(path):
	# ...could be a static file needed by the front end that
	# doesn't use the `static` path (like in `<script src="bundle.js">`)
	file_path = os.path.join(data_folder, path)
	print('mmserver: data_folder path:', data_folder)
	print('mmserver: /images path:', file_path)
	if os.path.isfile(file_path):
		return send_file(file_path)
	# ...or should be handled by the SPA's "router" in front end
	else:
		#index_path = os.path.join(app.static_folder, 'index.html')
		#return send_file(index_path)
		errorStr = 'mmserver error: did not find path: ' + file_path
		print(errorStr)
		return errorStr
		
@app.route('/download')
def download():
	print('download()')
	return render_template('download.html')

@app.route('/help')
def help():
	#todo: make this an html template and pass server ip
	theRet = ''
	theRet = 'This is the mmserver REST interface. It is designed to respond to http addresses and return data. It is not designed to be interacted directly by a user. <BR>'
	theRet += '<BR>'
	theRet += 'The time is ' + str(datetime.now()) + '<br>' \
		+ '/plot' + '<br>' \
		+ '/[username]/[mapname]/header' + '<br>' \
		+ '/[username]/[mapname]/timepoint/[n]/stackdb' + '<br>' \
		+ '/[username]/[mapname]/timepoint/[n]/image/[n]/[channel]' + '<br>'
	return theRet
	
@app.route('/api/v1/status')
def status():
	return 'ok'
	
@app.route('/api/v1/maplist/<username>')
def maps(username):
	"""
	Get a list of maps
	
	returns a list of folders in username folder
	"""
	print('maps username:', username)
	maplist = []
	userfolder = safe_join(app.config['data_folder'],username)
	if os.path.isdir(userfolder):
		maplist = [f for f in os.listdir(userfolder) if not f.startswith('.')]
	return json.dumps(maplist)

@app.route('/api/v1/downloadmap/<username>/<mapname>')
def downloadmap(username, mapname):
	mapdir = safe_join(app.config['data_folder'], username)
	mapzip = mapname + '.zip'
	thepath = safe_join(mapdir, mapzip)
	print('downloadmap:', thepath)
	return send_file(thepath)
	
@app.route('/api/v1/loadmap/<username>/<mapname>')
def loadmap(username, mapname):
	"""
	Load a map
	"""
	print('=== loadmap()')
	mapdir = safe_join(username, mapname)
	mapdir = safe_join(app.config['data_folder'], mapdir)
	mapfile = mapname + '.txt'
	mappath = safe_join(mapdir, mapfile)
	
	mapInfo = None
	
	# was this 20180118
	#global myMapList
	#if mapname in myMapList:
	if db.exists(mapname):
		# already loaded
		print('map already loaded')
		
		# get map info
		m = pickle.loads(db.get(mapname))
		mapInfo = m.mapInfo()
	else:
		print('loadmap() loading map:', mappath)
		# was this 20180118
		#myMapList[mapname] = mmMap(mappath)

		m = mmMap(mappath)
		pickled_object = pickle.dumps(m)
		db.set(mapname, pickled_object) # themap is a string key '' here

		mapInfo = m.mapInfo()
		print('loaded myMap:', mappath)
	
	# rr30a is 24 MB -> 0.024 GB. Telling us we can store ~41 maps in 1 GB
	#pickled_object = pickle.dumps(myMapList[mapname])
	#print('getsizeof:', sys.getsizeof(pickled_object))
	
	# was this 20180118
	#ret = myMapList[mapname].mapInfo() # enclose in dict?
	#return jsonify(ret)
	return jsonify(mapInfo)
	
@app.route('/api/v1/getmapvalues/<username>/<mapname>')
def getmapvalues(username, mapname):
	"""
	Get annotations from a map
	"""
	mapsegment = request.args.get('mapsegment', '')
	session = request.args.get('session', '')
	xstat = request.args.get('xstat', '')
	ystat = request.args.get('ystat', '')
	zstat = request.args.get('zstat', '')

	print('getmapvalues() mapsegment:', mapsegment, 'session:', session, 'xstat:', xstat, 'ystat:', ystat, 'zstat:', zstat)

	ret = {}
	
	pd = mmUtil.newplotdict()
	if mapsegment:
		pd['segmentid'] = int(mapsegment)
	else:
		pd['segmentid'] = None
	if session:
		pd['stacklist'] = [int(session)]
	else:
		pd['stacklist'] = []
	pd['xstat'] = xstat
	pd['ystat'] = ystat
	pd['zstat'] = zstat
	
	# for now, read xxx and if empty assume 'spineROI'
	'''
	if roitype:
		pd['roitype'] = [roiType]
	else:
		# get the default roi type for this map
		# if there is none, assume 'spineROI'
		pd['roitype'] = ['spineROI']
	'''
	
	# always fetch map dynamics into pd['dynamics']
	pd['getMapDynamics'] = True
	
	# always fetch bad
	pd['plotbad'] = True
	
	# debug
	if 0:
		print('getmapvalues pd:')
		for key, item in pd.iteritems():
			print('\t', key, ':', item)
		
	#print 'getmapvalues() pd:', pd
	#global myMapList
	#if mapname in myMapList:
	if db.exists(mapname):
		# get from redis
		m = pickle.loads(db.get(mapname))
		
		#defaultAnnotation = myMapList[mapname].defaultAnnotation
		defaultAnnotation = m.defaultAnnotation
		if defaultAnnotation:
			pd['roitype'] = defaultAnnotation
		else:
			pd['roitype'] = 'spineROI'
		
		print("getmapvalues() using pd['roitype']=", pd['roitype'])
		
		#pd = myMapList[mapname].getMapValues3(pd)
		pd = m.getMapValues3(pd)
		
		ret['x'] = pd['x']
		ret['y'] = pd['y']
		ret['z'] = pd['z']
		ret['mapsegment'] = pd['mapsegment']
		ret['stackidx'] = pd['stackidx']
		ret['mapsess'] = pd['mapsess']
		ret['dynamics'] = pd['dynamics']
		ret['cPnt'] = pd['cPnt']
		ret['isBad'] = pd['isBad']
		
		# remove nan AND flatten to list
		#print 'getmapvalues()', ret['x'].dtype # this is float64
		ret['x'] = ret['x'].astype('str').tolist()
		ret['y'] = ret['y'].astype('str').tolist()
		ret['z'] = ret['z'].astype('str').tolist()
		if len(ret['mapsegment']) > 0:
			ret['mapsegment'] = ret['mapsegment'].astype('str').tolist()
		ret['stackidx'] = ret['stackidx'].astype('str').tolist()
		ret['mapsess'] = ret['mapsess'].astype('str').tolist()
		ret['dynamics'] = ret['dynamics'].astype('str').tolist()
		ret['cPnt'] = ret['cPnt'].astype('str').tolist()
		ret['isBad'] = ret['isBad'].astype('str').tolist()
		#print ret['x']
	else:
		print('warning: getmapvalues(): map', mapname, 'is not loaded')
	#print 'getmapvalues:', ret
	return jsonify(ret)

@app.route('/api/v1/getmaptracing/<username>/<mapname>/')
def getmaptracing(username, mapname):
	"""
	Get x/y/z values of tracing
	"""
	mapsegment = request.args.get('mapsegment', '')
	session = request.args.get('session', '')
	
	# print 'getmaptracing() mapsegment:', mapsegment, mapsegment == None
	
	ret = {}
	#global myMapList
	#if mapname in myMapList:
	if db.exists(mapname):
		pd = mmUtil.newplotdict()
		if mapsegment:
			pd['segmentid'] = int(mapsegment)
		else:
			pd['segmentid'] = None
		if session:
			pd['stacklist'] = [int(session)]
		else:
			pd['stacklist'] = []
		
		session = int(session)

		# get from redis
		m = pickle.loads(db.get(mapname))
		pd = m.stacks[session].line.getLineValues3(pd)		

		# returns pd['x'] == None when no tracing
		#pd = myMapList[mapname].stacks[session].line.getLineValues3(pd)		
		
		ret['x'] = []
		ret['y'] = []
		ret['z'] = []
		
		if pd['x'] is not None:
			ret['x'] = pd['x'][:]
			ret['y'] = pd['y'][:]
			ret['z'] = pd['z'][:]
			ret['sDist'] = pd['sDist'][:]
			ret['ID'] = pd['ID'][:]
			
			# remove nan
			ret['x'] = ret['x'][~np.isnan(ret['x'])].tolist()
			ret['y'] = ret['y'][~np.isnan(ret['y'])].tolist()
			ret['z'] = ret['z'][~np.isnan(ret['z'])].tolist()
			ret['sDist'] = ret['sDist'][~np.isnan(ret['sDist'])].tolist()
			ret['ID'] = ret['ID'][~np.isnan(ret['ID'])].tolist()
	else:
		print('warning: getmaptracing(): map', mapname, 'is not loaded')
	return jsonify(ret)

@app.route('/api/v1/getimage/<username>/<mapname>/<int:timepoint>/<int:channel>/<int:slice>')
def get_image(username, mapname, timepoint, channel, slice):
	"""
	Get an image (slice) from a stack
	"""
	
	# http://127.0.0.1:5010/getimage/public/rr30a/0/1/5
	sliceStr = str(slice).zfill(4)
	thefile = mapname + '_tp' + str(timepoint) + '_ch' + str(channel) + '_s' + sliceStr + '.png'

	tpdir = safe_join(username, mapname)
	tpdir = safe_join(tpdir, 'raw')
	tpdir = safe_join(tpdir, 'ingested')
	tpdir = safe_join(tpdir, 'tp' + str(timepoint))
	tpdir = safe_join(app.config['data_folder'], tpdir)

	'''
	print('=== get_image()', username, mapname, timepoint, slice, channel)
	print('tpdir:', tpdir)
	print('thefile:', thefile)
	'''
	
	return send_from_directory(tpdir, thefile, as_attachment=True, mimetype='image/png')

@app.route('/api/v1/getslidingz/<username>/<mapname>/<int:timepoint>/<int:channel>/<int:slice>')
def getslidingz(username, mapname, timepoint, channel, slice):
	"""
	Get a generated image as a png by
	saving it into a StringIO and using send_file.
	"""
	plusMinus = 2
	# print '=== getslidingz() slice:', slice, 'plusMinus:', plusMinus
	
	# the folder the images are in
	tpdir = safe_join(username, mapname)
	tpdir = safe_join(tpdir, 'raw')
	tpdir = safe_join(tpdir, 'ingested')
	tpdir = safe_join(tpdir, 'tp' + str(timepoint))
	tpdir = safe_join(app.config['data_folder'], tpdir)

	#print '= getslidingz() tpdir:', tpdir
	
	# load the central image (we know it exists)
	paddedStr = str(slice).zfill(4)
	centralImageFile = tpdir + '/' + mapname + '_tp' + str(timepoint) + '_ch' + str(channel) + '_s' + paddedStr + '.png'

	myArray = imread(centralImageFile) #, flatten=False, mode=None)
	[m, n] = myArray.shape
	myArray = myArray.reshape((1,m,n))
	
	startSlice = slice - plusMinus
	stopSlice = slice + plusMinus
	firstTimeThrough = 1
	for i in range(startSlice,stopSlice):
		if i<0:
			continue
		paddedStr = str(i).zfill(4)
		currFile = tpdir + '/' + mapname + '_tp' + str(timepoint) + '_ch' + str(channel) + '_s' + paddedStr + '.png'
		#print 'currFile:', currFile
		if os.path.isfile(currFile):
			currArray = imread(currFile) #, flatten=False, mode=None)
			currArray = currArray.reshape((1,m,n))
			if firstTimeThrough:
				firstTimeThrough = 0
				myArray = currArray
			else:
				myArray = np.vstack((myArray,currArray)) 
				#myArray = np.vstack([myArray,currArray]) 
	
	# print 'myArray.shape:', myArray.shape
			
	# take maximal intensity projection into final nd array
	[slicesFinal, mFinal, nFinal] = myArray.shape
	max_ = np.zeros((m, n), dtype='uint8')
	for i in range(slicesFinal):
		max_ = np.maximum(max_, myArray[i])
	
	# We make sure to use the PIL plugin here because not all skimage.io plugins
	# support writing to a file object.
	try:
		strIO = StringIO()
		imsave(strIO, max_, plugin='pil', format_str='png')
		strIO.seek(0)
	except:
		print('\r\r\tmmserver.getslidingz() exception\r\r')
	return send_file(strIO, mimetype='image/png')

@app.route('/api/v1/getmaximage/<username>/<mapname>/<int:timepoint>/<int:channel>')
def get_maximage(username, mapname, timepoint, channel):
	"""
	Get the maximal intensity projection image
	"""

	#print '=== get_maximage()', username, mapname, timepoint, channel

	thefile = 'MAX_' + mapname + '_tp' + str(timepoint) + '_ch' + str(channel) + '.png'

	tpdir = safe_join(username, mapname)
	tpdir = safe_join(tpdir, 'raw')
	tpdir = safe_join(tpdir, 'ingested')
	tpdir = safe_join(app.config['data_folder'], tpdir)

	#print 'tpdir:', tpdir
	#print 'thefile:', thefile
	
	return send_from_directory(tpdir, thefile, as_attachment=True, mimetype='image/png')
		
############################################################
############################################################
# mmio is easier with files (compared to json as returned in /api/v1
############################################################
############################################################

@app.route('/api/v1/getfile/<item>/<username>/<mapname>')
@app.route('/api/v1/getfile/<item>/<username>/<mapname>/<timepoint>')
@app.route('/api/v1/getfile/<item>/<username>/<mapname>/<timepoint>/<int:channel>')
def getfile(item, username, mapname, timepoint=None, channel=None):
	"""
	Get a file from a map
	
	Arguments:
		item: (str) in ['header', 'objmap', 'segmap', 'stackdb', 'line', 'int'
		
		For ['stackdb', 'line', 'int'], must also specify 'timepoint'
		For ['int'], must also specify 'channel'
		
	Returns:
		File like string
	"""
		
	mapdir = safe_join(username, mapname)
	mapdir = safe_join(app.config['data_folder'], mapdir)
	
	as_attachment = False
	theFolder = '' # for timepoint files
	
	#
	# map
	#
	if item == 'header':
		mapfile = mapname + '.txt'
	elif item == 'objmap':
		mapfile = mapname + '_objMap.txt'
	elif item == 'segmap':
		mapfile = mapname + '_segMap.txt'
	elif item == 'zip':
		mapfile = mapname + '.zip'
		as_attachment = True
	#
	# timepoint
	#
	elif item == 'stackdb':
		mapfile = mapname + '_s' + str(timepoint) + '_db2.txt'
		theFolder = 'stackdb'
	elif item == 'line':
		mapfile = mapname + '_s' + str(timepoint) + '_l.txt'
		theFolder = 'line'
	elif item == 'int':
		mapfile = mapname + '_s' + str(timepoint) + '_Int' + str(channel) + '.txt'
		theFolder = 'stackdb'
	else:
		# error
		mapfile = ''

	if theFolder:
		mapdir = safe_join(mapdir, theFolder)
		
	if debugThis:
		print('=== mmserver.getfile()', item, username, mapname, timepoint, channel)
		print('   mapdir:', mapdir)
		print('   mapfile:', mapfile)
		
	return send_from_directory(mapdir, mapfile, as_attachment=True, attachment_filename=mapfile)
		

############################################################
############################################################
# post
############################################################
############################################################

ALLOWED_EXTENSIONS = set(['txt', 'tif'])

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/v1/uploadzip/<username>', methods=['GET', 'POST'])
def uploadzip(username):
	if request.method == 'POST':
		# user upload a zip
		print('mmserver POST /api/v1/uploadzip/')
		print('request.files:', request.files)
		files = request.files.getlist('file') # files on lhs, file on rhs
		print(files)
		
		# see: https://stackoverflow.com/questions/15981637/flask-how-to-handle-application-octet-stream
		for file in files:
			print('file:', file)
			print('file.filename:', file.filename)

			if not isinstance(file, FileStorage):
				raise TypeError("mmserver.uploadzip() storage must be a werkzeug.FileStorage")
			saveFileName = secure_filename(file.filename)
			savePath = os.path.join(UPLOAD_FOLDER, saveFileName)
			file.save(savePath)
		
		'''
		# unzip the .zip file
		import zipfile
		zip_ref = zipfile.ZipFile(savePath, 'r')
		zip_ref.extractall(directory_to_extract_to)
		zip_ref.close()
		'''
		
		# unzip the .zip file
		import zipfile
		dstZipFolder = safe_join(app.config['data_folder'],username)
		with zipfile.ZipFile(savePath,"r") as zip_ref:
			zip_ref.extractall(dstZipFolder)
		
		return 'ok'
	elif request.method == 'GET':
		# user download a zip
		print('mmserver GET /api/v1/uploadzip/')
		pass
	
@app.route('/post/<username>/<mapname>/<item>', methods=['GET', 'POST'])
def post_file(username, mapname, item):
	if request.method == 'POST':
		file = request.files['file']
		print('post_file() got request.files::', request.files)
		if file and allowed_file(file.filename):
			
			# todo: do something here for security
			#filename = secure_filename(file.filename)
			filename = file.filename
			
			filePath = os.path.join(app.config['UPLOAD_FOLDER'], username)
			# path to username has to exist, don't create it
			if not os.path.isdir(filePath):
				errStr = 'error: post_file() username does not exist:' + username
				print(errStr)
				return errStr
			filePath = os.path.join(filePath, mapname)
			# make map folder if necc.
			if not os.path.isdir(filePath):
				os.makedirs(filePath)
			if item == 'header':
				pass
			elif item == 'stackdb':
				filePath = os.path.join(filePath, 'stackdb')
				if not os.path.isdir(filePath):
					os.makedirs(filePath)
			elif item == 'line':
				filePath = os.path.join(filePath, 'line')
				if not os.path.isdir(filePath):
					os.makedirs(filePath)

			# save file on server in correct spot
			filePath = os.path.join(filePath,filename)
			print('post_file() saving file:', filePath)

			file.save(filePath)

			retStr = 'post_file() saved to: ' + filePath
			#return redirect(url_for('uploaded_file', filename=filename))
			return retStr
	else:
		retStr = 'error: post_file() got bad request.method:' + request.method
		return retStr

############################################################
# 
############################################################

@app.route("/plot2")
def plot2():
	# using bokeh, does not work, requires a dynamic <script> in angular
	plot = figure(plot_width=400, plot_height=400)
	plot.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="navy", alpha=0.5)
	script, div = components(plot)
	response = {}
	response['script'] = script
	response['div'] = div
	print('plot2()', response)
	return jsonify(response)

############################################################
# main
############################################################
if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000, debug=True)

