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
import os
import json
from datetime import datetime

try:
    from cStringIO import StringIO # python 2.x
except ImportError:
    from io import StringIO # python 3.x

from flask import Flask, render_template, send_file, send_from_directory, safe_join
from flask import jsonify, request
from flask_cors import CORS

import pandas as pandas
import numpy as np
from skimage.io import imsave, imread

from pymapmanager import mmMap, mmUtil

# local debugging
debugThis = False

# turn off printing to console
if 0:
	import logging
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)

# assuming data folder is in same folder as this source .py file
UPLOAD_FOLDER = '../../PyMapManager-Data/upload'
data_folder = '../../PyMapManager-Data'

# load a default map, leave this here until I implement redis
# to share myMapList between processes
myMapList = {}
if 1:
	defaultMapPath = data_folder + '/public/rr30a/rr30a.txt'
	myMapList['rr30a'] = mmMap(defaultMapPath)

############################################################
# app
############################################################
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # upload to server should be proper scp, then flask app can trigger mmMap.ingest
app.config['data_folder'] = data_folder

############################################################
# routes
############################################################
@app.route('/')
def hello_world():
	print('hello_world()')
	#return render_template('index.html')
	return 'mmserver rest interface. use /help to get started'

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
	
	global myMapList
	if mapname in myMapList:
		# already loaded
		print('map already loaded')
		pass
	else:
		print('loadmap() loading map:', mappath)
		myMapList[mapname] = mmMap(mappath)
		print('loaded myMap:', myMapList[mapname])
	ret = myMapList[mapname].mapInfo() # enclose in dict?
	return jsonify(ret)

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
	
	# debug
	if 0:
		print('getmapvalues pd:')
		for key, item in pd.iteritems():
			print('\t', key, ':', item)
		
	#print 'getmapvalues() pd:', pd
	global myMapList
	if mapname in myMapList:
		defaultAnnotation = myMapList[mapname].defaultAnnotation
		if defaultAnnotation:
			pd['roitype'] = defaultAnnotation
		else:
			pd['roitype'] = 'spineROI'
		
		print("getmapvalues() using pd['roitype']=", pd['roitype'])
		
		pd = myMapList[mapname].getMapValues3(pd)
		
		ret['x'] = pd['x']
		ret['y'] = pd['y']
		ret['z'] = pd['z']
		ret['mapsegment'] = pd['mapsegment']
		ret['stackidx'] = pd['stackidx']
		ret['mapsess'] = pd['mapsess']
		ret['dynamics'] = pd['dynamics']
		ret['cPnt'] = pd['cPnt']
		
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
	global myMapList
	if mapname in myMapList:
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
		# returns pd['x'] == None when no tracing
		pd = myMapList[mapname].stacks[session].line.getLineValues3(pd)
		
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
		print('\r\r\t\tgetslidingz() exception\r\r')
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
	app.run(host='0.0.0.0',port=5010, debug=True)

