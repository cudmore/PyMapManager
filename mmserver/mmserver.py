"""
Author: Robert Cudmore
Date: 20170808

A http server to serve mmMap files and images.
Server is run using Flask.
Implements a RESTful API.

http://cudmore.duckdns.org:5010/public/rr30a/header
http://cudmore.duckdns.org:5010/public/rr30a/objmap
http://cudmore.duckdns.org:5010/public/rr30a/segmap
http://cudmore.duckdns.org:5010/public/rr30a/1/stackdb
http://cudmore.duckdns.org:5010/public/rr30a/1/int/2
http://cudmore.duckdns.org:5010/public/rr30a/1/line
http://cudmore.duckdns.org:5010/public/rr30a/1/image/10/2
http://cudmore.duckdns.org:5010/public/rr30a/zip

mmio is a Python wrapper to provide easy programming interface to the REST api

todo:
	there should be two main routes here: api and data
	- api: is for javascript to get json data
	- data: is for python to get files
	
	add another playground route to plot directly off server
	
"""

import os
import json
from datetime import datetime

from flask import Flask, render_template, make_response, send_file, send_from_directory, safe_join
from flask import jsonify, request, redirect, url_for
from flask_cors import CORS
# from werkzeug.utils import secure_filename

import pandas as pandas
import numpy as np

from cStringIO import StringIO # for sending a numpy array back as a .png image
from skimage.io import imsave, imread

#from bokeh.plotting import figure, output_file, show
#from bokeh.embed import components

from pymapmanager import mmMap
from pymapmanager import mmUtil

# turn off printing to console
if 1:
	import logging
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)

# assuming data folder is in same folder as this source .py file
#static_folder = '/Users/cudmore/Desktop/data'
template_dir = os.path.abspath('../mmclient')
static_folder = './data'
UPLOAD_FOLDER = './data'
data_folder = './data'

#myMap = None
myMapList = {}

#app = Flask(__name__, static_url_path='/data')
#app = Flask(__name__, static_folder=static_folder)
app = Flask(__name__, template_folder=template_dir)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['data_folder'] = data_folder

@app.route('/')
def hello_world():
	print 'hello_world()'
	return render_template('index.html')

'''
@app.route('/purejs')
def hello_world2():
	print 'hello_world2()'
	return render_template('purejs/index.html')
'''

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
	
@app.route('/loadmap/<username>/<mapname>')
def loadmap(username, mapname):
	print ('=== loadmap()')
	mapdir = safe_join(username, mapname)
	mapdir = safe_join(app.config['data_folder'], mapdir)
	mapfile = mapname + '.txt'
	mappath = safe_join(mapdir, mapfile)
	
	global myMapList
	if mapname in myMapList:
		# already loaded
		print 'map already loaded'
		pass
	else:
		print 'loadmap() loading map:', mappath
		myMapList[mapname] = mmMap.mmMap(mappath)
		print 'myMap:', myMapList[mapname]
	ret = mapInfo(mapname)
	return jsonify(ret)

def mapInfo(mapname):
	theRet = {}
	if mapname in myMapList:
		theRet = myMapList[mapname].mapInfo()
		# tweak 2d arrays for json
		theRet['objMap'] = theRet['objMap'].astype('str').tolist() # spine i, session j, [i][j] gives us runIdx
		theRet['runMap'] = theRet['runMap'].astype('str').tolist() # run index i, session j, [i][j] gives us stack idx
		theRet['segMap'] = theRet['segMap'].astype('str').tolist()
	else:
		print 'error: mapInfo() map not loaded:', mapname
	#return json.dumps(theRet)
	return theRet
	
@app.route('/api/<username>/maps')
def maps(username):
	# return a list of folders in username folder
	print 'maps:', username
	maplist = []
	userfolder = safe_join(static_folder,username)
	if os.path.isdir(userfolder):
		maplist = [f for f in os.listdir(userfolder) if not f.startswith('.')]
	return json.dumps(maplist)

@app.route('/api/<username>/<mapname>/<item>')
def get_header(username, mapname, item):
	# return a top level file of a map
	# args: item (str): one of (header, objmap, segmap)
		
	mapdir = safe_join(username, mapname)
	mapdir = safe_join(app.static_folder, mapdir)
	
	as_attachment = False
	if item == 'header':
		mapfile = mapname + '.txt'
	elif item == 'objmap':
		mapfile = mapname + '_objMap.txt'
	elif item == 'segmap':
		mapfile = mapname + '_segMap.txt'
	elif item == 'zip':
		mapfile = mapname + '.zip'
		as_attachment = True
	else:
		mapfile = ''

	print '=== get_header()', username, mapname, item
	print 'mapdir:', mapdir
	print 'mapfile:', mapfile
	return send_from_directory(mapdir, mapfile, as_attachment=True, attachment_filename=mapfile)
	#return send_from_directory(mapdir, mapfile) #, as_attachment=as_attachment) #, mimetype='text/txt')

'''
@app.route('/v2/<username>/<mapname>/getmapdynamics')
def getmapdynamics(username, mapname):
	mapsegment = request.args.get('mapsegment', '')
	session = request.args.get('session', '')

	pd = mmUtil.newplotdict()
	if mapsegment:
		pd['segmentid'] = int(mapsegment)
	else:
		pd['segmentid'] = None
	if session:
		pd['stacklist'] = [int(session)]
	else:
		pd['stacklist'] = []

	ret = {}

	global myMapList
	if mapname in myMapList:
		pd = myMapList[mapname].getMapDynamics(pd)
		ret['dynamics'] = pd['dynamics']
		ret['mapsegment'] = pd['mapsegment']
		ret['stackidx'] = pd['stackidx']
		ret['mapsess'] = pd['mapsess']

		ret['dynamics'] = ret['dynamics'].astype('str').tolist()
		ret['mapsegment'] = ret['mapsegment'].astype('str').tolist()
		ret['stackidx'] = ret['stackidx'].astype('str').tolist()
		ret['mapsess'] = ret['mapsess'].astype('str').tolist()

	else:
		print 'warning: getmapvalues(): map', mapname, 'is not loaded'

	return jsonify(ret)
'''
		
@app.route('/v2/<username>/<mapname>/getmapvalues')
def getmapvalues(username, mapname):
	mapsegment = request.args.get('mapsegment', '')
	session = request.args.get('session', '')
	xstat = request.args.get('xstat', '')
	ystat = request.args.get('ystat', '')
	zstat = request.args.get('zstat', '')

	print 'getmapvalues() mapsegment:', mapsegment, 'session:', session, 'xstat:', xstat, 'ystat:', ystat, 'zstat:', zstat

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
	
	# always detch map dynamics into pd['dynamics']
	pd['getMapDynamics'] = True
	
	#print 'getmapvalues() pd:', pd
	global myMapList
	if mapname in myMapList:
		pd = myMapList[mapname].getMapValues3(pd)
		
		doFlatten = 0
		if doFlatten:
			ret['x'] = pd['x'][:]
			ret['y'] = pd['y'][:]
			ret['z'] = pd['z'][:]
			ret['mapsegment'] = pd['mapsegment'][:]
			ret['stackidx'] = pd['stackidx'][:]
			ret['mapsess'] = pd['mapsess'][:]
		else:
			ret['x'] = pd['x']
			ret['y'] = pd['y']
			ret['z'] = pd['z']
			ret['mapsegment'] = pd['mapsegment']
			ret['stackidx'] = pd['stackidx']
			ret['mapsess'] = pd['mapsess']
			ret['dynamics'] = pd['dynamics']
			ret['cPnt'] = pd['cPnt']
		# remove nan AND flatten to list
		if 0:
			ret['x'] = ret['x'][~np.isnan(ret['x'])].tolist()
			ret['y'] = ret['y'][~np.isnan(ret['y'])].tolist()
			ret['z'] = ret['z'][~np.isnan(ret['z'])].tolist()
			ret['mapsegment'] = ret['mapsegment'][~np.isnan(ret['mapsegment'])].tolist()
			ret['stackidx'] = ret['stackidx'][~np.isnan(ret['stackidx'])].tolist()
			ret['mapsess'] = ret['mapsess'][~np.isnan(ret['mapsess'])].tolist()
			#print ret['x']
		if 1:
			#print 'getmapvalues()', ret['x'].dtype # this is float64
			ret['x'] = ret['x'].astype('str').tolist()
			ret['y'] = ret['y'].astype('str').tolist()
			ret['z'] = ret['z'].astype('str').tolist()
			ret['mapsegment'] = ret['mapsegment'].astype('str').tolist()
			ret['stackidx'] = ret['stackidx'].astype('str').tolist()
			ret['mapsess'] = ret['mapsess'].astype('str').tolist()
			ret['dynamics'] = ret['dynamics'].astype('str').tolist()
			ret['cPnt'] = ret['cPnt'].astype('str').tolist()
			#print ret['x']
	else:
		print 'warning: getmapvalues(): map', mapname, 'is not loaded'
	#print 'getmapvalues:', ret
	return jsonify(ret)

@app.route('/v2/<username>/<mapname>/getmaptracing')
def getmaptracing(username, mapname):
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
		pd = myMapList[mapname].stacks[session].line.getLineValues3(pd)
		
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
		print 'warning: getmaptracing(): map', mapname, 'is not loaded'
	return jsonify(ret)
		
@app.route('/v2/<username>/<mapname>/<item>')
def get_header_v2(username, mapname, item):
	# return a top level file of a map
	# args: item (str): one of (header, objmap, segmap)
		
	mapdir = safe_join(username, mapname)
	mapdir = safe_join(app.config['data_folder'], mapdir)
	
	as_attachment = False
	if item == 'header':
		print '   get_header_v2: header'
		mapfile = mapname + '.txt'
		path = mapdir + '/' + mapfile
		print '   path:', path
		t = pandas.read_table(path, index_col=0)
		return t.to_json()
	elif item == 'sessions':
		mapfile = mapname + '.txt'
		path = mapdir + '/' + mapfile
		print '   path:', path
		t = pandas.read_table(path, index_col=0)
		#ret = {}
		ret = []
		for idx, i in enumerate(t.loc['hsStack']):
			if str(i) != 'nan':
				#ret.append({'s'+str(idx) : i})
				#ret.append({idx : i})
				ret.append(i)
				#ret['s' + str(idx)] = i
		#print 'ret:', ret
		#print jsonify(ret)
		#return jsonify(ret)
		return jsonify(ret)
	elif item == 'mapsegments':
		global myMapList
		if mapname in myMapList:
			numRows = myMapList[mapname].segRunMap.shape[0]
			ret = []
			for i in range(numRows):
				ret.append(i)
			return jsonify(ret)
		else:
			# map not loaded
			return jsonify('')
	elif item == 'objmap':
		mapfile = mapname + '_objMap.txt'
	elif item == 'segmap':
		mapfile = mapname + '_segMap.txt'
	elif item == 'zip':
		mapfile = mapname + '.zip'
		as_attachment = True
		
	print '=== get_header()', username, mapname, item
	print 'mapdir:', mapdir
	print 'mapfile:', mapfile
	return send_from_directory(mapdir, mapfile, as_attachment=True, attachment_filename=mapfile)
	#return send_from_directory(mapdir, mapfile) #, as_attachment=as_attachment) #, mimetype='text/txt')

@app.route('/api/<username>/<mapname>/<timepoint>/<item>')
@app.route('/api/<username>/<mapname>/<timepoint>/<item>/<int:channel>')
def get_file(username, mapname, timepoint, item, channel=None):
	# return a file for single timepoint
	# args: item (str): Is one of (stackdb, line, int)
		
	if item == 'stackdb':
		thefile = mapname + '_s' + str(timepoint) + '_db2.txt'
		thefolder = 'stackdb'
	elif item == 'line':
		thefile = mapname + '_s' + str(timepoint) + '_l.txt'
		thefolder = 'line'
	elif item == 'int':
		thefile = mapname + '_s' + str(timepoint) + '_Int' + str(channel) + '.txt'
		thefolder = 'stackdb'
	else:
		# error
		thefile = ''
		thefolder = ''
	
	tpdir = safe_join(username, mapname)
	tpdir = safe_join(tpdir, thefolder)
	tpdir = safe_join(app.static_folder, tpdir)

	print '=== getfile()', username, mapname, timepoint, item, channel
	print tpdir
	print thefile
	
	return send_from_directory(tpdir, thefile)

@app.route('/getimage/<username>/<mapname>/<int:timepoint>/<int:channel>/<int:slice>')
def get_image(username, mapname, timepoint, channel, slice):
	# get an image (slice) from a stack
	# http://127.0.0.1:5010/getimage/public/rr30a/0/1/5
	sliceStr = str(slice).zfill(4)
	thefile = mapname + '_tp' + str(timepoint) + '_ch' + str(channel) + '_s' + sliceStr + '.png'
	#thefolder = 'raw'

	tpdir = safe_join(username, mapname)
	tpdir = safe_join(tpdir, 'raw')
	tpdir = safe_join(tpdir, 'ingested')
	tpdir = safe_join(tpdir, 'tp' + str(timepoint))
	tpdir = safe_join(app.config['data_folder'], tpdir)

	'''
	print '=== get_image()', username, mapname, timepoint, slice, channel
	print 'tpdir:', tpdir
	print 'thefile:', thefile
	'''
	
	return send_from_directory(tpdir, thefile, as_attachment=True, mimetype='image/png')

# 20171227, returning a numpy array as a .png
# for now, sliding z will be three images [slice-1, slice, slice+1]
#@app.route('/getslidingz')
# http://127.0.0.1:5010/getslidingz/public/rr30a/1/2/20
@app.route('/getslidingz/<username>/<mapname>/<int:timepoint>/<int:channel>/<int:slice>')
def getslidingz(username, mapname, timepoint, channel, slice):
	"""
	Return a generated image as a png by
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
		print '\r\r\t\tgetslidingz() exception\r\r'
	return send_file(strIO, mimetype='image/png')

@app.route('/getmaximage/<username>/<mapname>/<int:timepoint>/<int:channel>')
def get_maximage(username, mapname, timepoint, channel):
	# get the max project
	# http://127.0.0.1:5010/getimage/public/rr30a/0/1/5
	# MAX_rr30a_tp0_ch2.jpg

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
# post
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
		print 'post_file() got request.files::', request.files
		if file and allowed_file(file.filename):
			
			# todo: do something here for security
			#filename = secure_filename(file.filename)
			filename = file.filename
			
			filePath = os.path.join(app.config['UPLOAD_FOLDER'], username)
			# path to username has to exist, don't create it
			if not os.path.isdir(filePath):
				errStr = 'error: post_file() username does not exist:' + username
				print errStr
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
			print 'post_file() saving file:', filePath

			file.save(filePath)

			retStr = 'post_file() saved to: ' + filePath
			#return redirect(url_for('uploaded_file', filename=filename))
			return retStr
	else:
		retStr = 'error: post_file() got bad request.method:' + request.method
		return retStr

############################################################
# post
############################################################

@app.route('/gettiff')
def gettiff():
	filename='data/rr30a/raw/rr30a_s0_ch2_0032.tif'
	#filename='img1.tif'
	file = 'rr30a_s0_ch2_0059.tif'
	return send_file(filename, mimetype='image/tif')
	#return send_from_directory('data/rr30a/raw', file

@app.route("/data")
def data():
	
	import numpy as np

	myarray = np.ones([1024,1024]).astype('uint16')

	output = StringIO()
	np.savetxt(output, myarray)
	csv_string = output.getvalue()
	print csv_string
	return csv_string

'''
@app.route("/plot")
def simple():
	# static figure using matplotlib
	import datetime
	import StringIO
	import random

	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	from matplotlib.dates import DateFormatter

	fig=Figure()
	ax=fig.add_subplot(111)
	x=[]
	y=[]
	now=datetime.datetime.now()
	delta=datetime.timedelta(days=1)
	for i in range(10):
		x.append(now)
		now+=delta
		y.append(random.randint(0, 1000))
	ax.plot_date(x, y, '-')
	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
	fig.autofmt_xdate()
	canvas=FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	response=make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response
'''

@app.route("/plot2")
def plot2():
	# using bokeh, does not work, requires a dynamic <script> in angular
	plot = figure(plot_width=400, plot_height=400)
	plot.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="navy", alpha=0.5)
	script, div = components(plot)
	response = {}
	response['script'] = script
	response['div'] = div
	print 'plot2()', response
	return jsonify(response)

@app.route("/my_d3")
def my_d3():
	#
	return render_template('my_d3.html')

@app.route("/myleaflet")
def myleaflet():
	return render_template('myleaflet.html')

if __name__ == '__main__':
	#gettiff()
	# host= '0.0.0.0' will run on servers network ip
	#app.run(host='0.0.0.0', port=5010)
	# this will run on localhost at port :5010
	app.run(host='0.0.0.0',port=5010, debug=True)

