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

Notes:
	Run with gunicorn
	sudo /usr/local/bin/gunicorn mmserver:app --worker-class gevent --workers 5 --timeout 400 --bind 127.0.0.1:5000

	--workers 5 = (num cores) * 2 + 1
	--timeout 400 = seconds, so /zip upload route does not time-out, will not work for HUGE files or SLOW connection

	Run redis
	redis-server

	Run celery
	celery worker -A mmserver.celery --loglevel=info
"""

from __future__ import print_function
import os, sys, time
import json
from datetime import datetime
#from collections import OrderedDict

try:
	from cStringIO import StringIO # python 2.x
except ImportError:
	from io import BytesIO as StringIO # python 3.x

# 20210922 removed safe_join
from flask import Flask, render_template, send_file, send_from_directory # , safe_join
from flask import jsonify, request, make_response, Response, url_for
from flask_cors import CORS

# 20210922 was this
#from werkzeug import secure_filename, FileStorage
# 20210922 added safe_join
from werkzeug.utils import secure_filename, safe_join
from werkzeug.datastructures import  FileStorage

import pandas as pandas
import numpy as np
from skimage.io import imsave, imread
import redis
import pickle
from celery import Celery

#import pymapmanager
#print('   mmserver: pymapmanager.__version__:', pymapmanager.__version__)

import random # for tesking celery, remove

from pymapmanager import mmMap, mmUtil

# local debugging
debugThis = False

# turn off printing to console
if 0:
	import logging
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)

############################################################
# Background thread
############################################################
#from threading import Thread
import zipfile

#myThread = Thread()

'''
import asyncio
import smtplib
from threading import Thread

def start_email_worker(loop):
	"""Switch to new event loop and run forever"""
	asyncio.set_event_loop(loop)
	loop.run_forever()
# Create the new loop and worker thread
worker_loop = asyncio.new_event_loop()
worker = Thread(target=start_email_worker, args=(worker_loop,))
worker.start() # Start the thread
'''

############################################################
# PyMapManager-Data
############################################################

# assuming PyMapManager-Data folder is in same folder as PyMapManager (they are in parallel)
UPLOAD_FOLDER = '../PyMapManager-Data/upload'
data_folder = '../PyMapManager-Data' # docker version

if __name__ == '__main__':
	# debug version
	data_folder = '../../PyMapManager-Data'
	UPLOAD_FOLDER = '../../PyMapManager-Data/upload'
else:
	# docker version
	data_folder = '../PyMapManager-Data'
	UPLOAD_FOLDER = '../PyMapManager-Data/upload'
	if not os.path.isdir(data_folder):
		# gunicorn version
		data_folder = '../../PyMapManager-Data'
		UPLOAD_FOLDER = '../../PyMapManager-Data/upload'

print('   mmserver data_folder:', data_folder)
############################################################
# app
############################################################
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # upload to server should be proper scp, then flask app can trigger mmMap.ingest
app.config['data_folder'] = data_folder

##########################################################
# Celery
# run at command line with
# celery worker -A mmserver.celery --loglevel=info
##########################################################

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task(bind=True)
def long_task(self, a1):
	"""Background task that runs a long function with progress reports."""
	print('=== celery long_task()')
	startEpoch = time.time()
	startDate = datetime.now().strftime('%Y%m%d')
	startTime = datetime.now().strftime('%H:%m:%S')

	print('startEpoch:', startEpoch, 'startDate:', startDate, 'startTime:', startTime)

	verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
	adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
	noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
	message = ''
	total = random.randint(10, 50)
	for i in range(total):
		elapsed = (time.time() - startEpoch) / 60 # minutes
		elapsed = round(elapsed,1)
		if not message or random.random() < 0.25:
			message = '{0} {1} {2}...'.format(random.choice(verb),
											  random.choice(adjective),
											  random.choice(noun))
		self.update_state(state='PROGRESS',
						  meta={'current': i,
						  		'total': total,
								'status': message,
								'startdate': startDate,
								'starttime': startTime,
								'elapsed (min)': elapsed,
								})
		time.sleep(1)
	return {'current': 100, 'total': 100, 'status': 'Task completed!',
			'startdate': startDate,
			'starttime': startTime,
			'elapsed (min)': elapsed,
			'result': 42}

@app.route('/longtask', methods=['POST', 'GET'])
def longtask():
	print('app.route /longtask')
	task = long_task.apply_async(args=['xxx'])
	print('task.id:', task.id)

	#db.rpush('tasklist', *[task.id.decode('UTF-8')])
	db.rpush('tasklist', *[task.id])

	#return jsonify({}), 202, {'Location': url_for('taskstatus',
	#											  task_id=task.id)}
	return task.id

@app.route('/status/<task_id>')
def taskstatus(task_id):
	#task = long_task.AsyncResult(task_id)
	task = background_thread.AsyncResult(task_id)
	if task.state == 'PENDING':
		# job did not start yet
		response = {
			'state': task.state,
			'map': '',
			'startdate': '',
			'starttime': '',
			'elapsed (min)': '',
			'status': 'Pending...'
		}
	elif task.state != 'FAILURE':
		#response = OrderedDict(task.info)
		response = {
			'state': task.state,
			'map': task.info.get('map', ''),
			'startdate': task.info.get('startdate', ''),
			'starttime': task.info.get('starttime', ''),
			'elapsed (min)': task.info.get('elapsed (min)', ''),
			'status': task.info.get('status', '')
		}
		if 'result' in task.info:
			response['result'] = task.info['result']
	else:
		# something went wrong in the background job
		response = {
			'state': task.state,
			'map': '',
			'startdate': '',
			'starttime': '',
			'elapsed (min)': '',
			'status': str(task.info),  # this is the exception raised
		}
	return json.dumps(response)

############################################################
# redis
############################################################
class fakeredis():
	"""
	Class to simulate redis. This way user does not have to be running redis for 'python mmserver.py'
	"""
	def __init__(self):
		self.dict = {}
	def exists(self, mapname):
		return mapname in self.dict
	def get(self, mapname):
		if mapname in self.dict:
			return self.dict[mapname]
		else:
			return ''
	def set(self, mapname, pickledata):
		self.dict[mapname] = pickledata
	# davis
	def ltrim(self, str1, int1, int2):
		pass

upTime = time.time()

if __name__ == '__main__':
	# debug version when run with 'python mmserver.py'
	#db = redis.StrictRedis(host='localhost', port=6379, db=0) #connect to redis server
	print('   mmserver is using fakeredis()')
	db = fakeredis()
else:
	# docker version
	platform = sys.platform
	if platform == "linux" or platform == "linux2":
		# linux
		db = redis.StrictRedis(host='redis', port=6379, db=0) #connect to redis server
	elif platform == "darwin":
		# OS X
		db = redis.StrictRedis(host='localhost', port=6379, db=0) #connect to redis server
	elif platform == "win32":
		# Windows...
		db = redis.StrictRedis(host='redis', port=6379, db=0) #connect to redis server

def db_set_str(token, str):
	pickled_object = pickle.dumps(str)
	db.set(token, pickled_object)

def db_get_str(token):
	ret = pickle.loads(db.get(token))
	return ret

db_set_str('ingesting', 'Idle')
db.ltrim('tasklist', 1, 0) # remove all elements

############################################################
# routes
############################################################
@app.errorhandler(404)
def not_found(error):
	theRet = {
		'name': 'mmserver',
		'error': 'Not found',
		'page': request.path,
		'datetime': str(datetime.now())
	}
	return make_response(jsonify(theRet), 404)

@app.route('/')
def hello_world():
	print('hello_world()')
	index_path = os.path.join(app.static_folder, 'index.html')
	#return('20210922 hello world')
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
	#print('mmserver: data_folder path:', data_folder)
	#print('mmserver: /images path:', file_path)
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
	path = os.path.join(app.static_folder, 'download.html')
	return send_file(path)

@app.route('/upload')
def upload():
	print('upload()')
	path = os.path.join(app.static_folder, 'upload.html')
	return send_file(path)

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
	theRet = {
		'name': 'mmserver',
		'uptime': datetime.fromtimestamp(upTime),
		'datetime': datetime.fromtimestamp(time.time())
	}
	#return make_response(jsonify(theRet), 404)
	return jsonify(theRet)

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
		for f in os.listdir(userfolder):
			if not os.path.isdir(userfolder + '/' + f):
				continue
			if f in ['__MACOSX']:
				continue
			if f.startswith('.'):
				continue
			maplist.append(f)
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

@celery.task(bind=True)
def background_thread(self, zipPath):
	print('   === background_thread() zipPath:', zipPath)

	startEpoch = time.time()
	startDate = datetime.now().strftime('%Y%m%d')
	startTime = datetime.now().strftime('%H:%m:%S')

	#zipFile.save(zipPath)

	username = 'public'
	# unzip the .zip file
	dstZipFolder = safe_join(app.config['data_folder'],username)
	zipFileName = os.path.basename(zipPath)
	mapName = os.path.splitext(zipFileName)[0]
	mapPath = dstZipFolder + '/' + mapName

	print('   unzipping ', zipPath)
	print('	  to ', dstZipFolder)
	print('	  mapName:', mapName)

	self.update_state(state='PROGRESS',
						meta={'map': mapName,
							'status': 'Unzipping',
							'startdate': startDate,
							'starttime': startTime,
							'elapsed (min)': '',
							})

	with zipfile.ZipFile(zipPath,"r") as zip_ref:
		zip_ref.extractall(dstZipFolder)

	print('done unzipping')

	print('   ingesting: ', mapPath)
	m = mmMap(mapPath)
	#m.ingest()
	for idx, stack in enumerate(m):
		elapsed = (time.time() - startEpoch) / 60 # minutes
		elapsed = round(elapsed,1)
		statusStr = 'Ingesting session ' + str(idx+1) + ' of ' + str(m.numSessions)
		print('statusStr:', statusStr)
		self.update_state(state='PROGRESS',
							meta={'map': mapName,
								'status': statusStr,
								'startdate': startDate,
								'starttime': startTime,
								'elapsed (min)': elapsed,
								})

		stack.ingest()


	print('   background_thread() done')

	return {'map': mapName,
			'status': 'Finished',
			'startdate': startDate,
			'starttime': startTime,
			'elapsed (min)': elapsed}

@app.route('/api/v1/uploadzip/<username>', methods=['GET', 'POST'])
def uploadzip(username):
	if request.method == 'POST':
		# user upload a zip
		print('=== mmserver POST /api/v1/uploadzip/')

		if 'file' in request.files:
			pass
		else:
			print('uploadzip() no file')
			return 'uploadzip() no file'

		file = request.files['file']
		filename = file.filename.encode("utf8")

		print('uploadzip() file:', file)
		print('uploadzip() filename:', filename)

		if request.files['file'].filename == '':
			return 'uploadzip() No selected file'
		try:
			img_file = request.files.get('file')
		except:
			return 'uploadzip() must upload a file'
		img_name = img_file.filename
		mimetype = img_file.content_type
		print('uploadzip()', 'img_name:', img_name, 'mimetype:', mimetype)
		#return 'zzz'
		if not 'file' in request.files:
			print('uploadzip() yyy')
			return jsonify({'error': 'no file'}), 400
		else:
			pass
			#return('xxx')

		files = request.files.getlist('file') # files on lhs, file on rhs
		print('   files:', files)

		# see: https://stackoverflow.com/questions/15981637/flask-how-to-handle-application-octet-stream
		for file in files:
			print('   file:', file)
			print('   file.filename:', file.filename)

			if not file.filename.endswith('.zip'):
				# error
				print('does not end in .zip')
				return Response('you must upload a .zip file',mimetype="text/event-stream")

			if not isinstance(file, FileStorage):
				print('is not isinstance')
				raise TypeError("mmserver.uploadzip() storage must be a werkzeug.FileStorage")
			saveFileName = secure_filename(file.filename)
			savePath = os.path.join(UPLOAD_FOLDER, saveFileName)

			print('saving file to:', savePath)

			file.save(savePath)

			print('done saving')

			#worker_loop.call_soon_threadsafe(background_thread, savePath)
			#print('*** SPAWNING THREAD background_thread() ***')
			#myThread = Thread(target=background_thread, args=[savePath])
			#myThread.start()

			#task = long_task.apply_async()
			print('spawning background_thread.apply_async')
			task = background_thread.apply_async(args=[savePath])
			db.rpush('tasklist', *[task.id])
			print('task.id:', task.id)

		print('uploadzip() returning')
		#return Response('ok', 200)
		return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

	elif request.method == 'GET':
		# user download a zip
		print('mmserver GET /api/v1/uploadzip/')
		pass
		#return 'GET'

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
# Server Side Event (sse)
############################################################
@app.route('/event_stream')
def stream():
	'''
	User a server side event (sse) to stream data back to the client.
	See EventSource in .js
	'''
	print('app.rout /event_stream')
	def event_stream():
		while True:
			time.sleep(1)
			#ingestStr = db_get_str('ingesting') #.decode("utf-8")
			tasklist = db.lrange('tasklist', 0, -1)
			tasklist2 = [taskstatus(x.decode('UTF-8')) for x in tasklist]
			yield "data: %s\n\n" % json.dumps(tasklist2)

	return Response(event_stream(), mimetype="text/event-stream")

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
	# /usr/local/bin/gunicorn mmserver:app --worker-class gevent --bind 127.0.0.1:5000
	app.run(host='0.0.0.0',port=5000, debug=True)
