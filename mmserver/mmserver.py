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

"""

import os
import json
from datetime import datetime

from flask import Flask, make_response, send_file, send_from_directory, safe_join
from flask import jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename

# assuming data folder is in same folder as this source .py file
#static_folder = '/Users/cudmore/Desktop/data'
static_folder = './data'
UPLOAD_FOLDER = './data'

#app = Flask(__name__, static_url_path='/data')
app = Flask(__name__, static_folder=static_folder)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def hello_world():
    print 'hello_world()'
    return 'Hello Fuckers. The time is ' + str(datetime.now()) + '<br>' \
    	+ '/plot' + '<br>' \
    	+ '/[username]/[mapname]/header' + '<br>' \
    	+ '/[username]/[mapname]/timepoint/[n]/stackdb' + '<br>' \
    	+ '/[username]/[mapname]/timepoint/[n]/image/[n]/[channel]' + '<br>' \


@app.route('/<username>/maps')
def maps(username):
	# return a list of folders in username folder
	print 'maps:', username
	maplist = []
	userfolder = safe_join(static_folder,username)
	if os.path.isdir(userfolder):
		maplist = [f for f in os.listdir(userfolder) if not f.startswith('.')]
	return json.dumps(maplist)

@app.route('/<username>/<mapname>/<item>')
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
		
	print '=== get_header()', username, mapname, item
	print 'mapdir:', mapdir
	print 'mapfile:', mapfile
	return send_from_directory(mapdir, mapfile, as_attachment=True, attachment_filename=mapfile)
	#return send_from_directory(mapdir, mapfile) #, as_attachment=as_attachment) #, mimetype='text/txt')

@app.route('/<username>/<mapname>/<timepoint>/<item>')
@app.route('/<username>/<mapname>/<timepoint>/<item>/<int:channel>')
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

	tpdir = safe_join(username, mapname)
	tpdir = safe_join(tpdir, thefolder)
	tpdir = safe_join(app.static_folder, tpdir)

	print '=== getfile()', username, mapname, timepoint, item, channel
	print tpdir
	print thefile
	
	return send_from_directory(tpdir, thefile)

@app.route('/<username>/<mapname>/<timepoint>/image/<slice>/<int:channel>')
def get_image(username, mapname, timepoint, slice=None, channel=None):
	# rr30a_s0_ch1.tif
	thefile = mapname + '_s' + str(timepoint) + '_ch' + str(channel) + '.tif'
	thefolder = 'raw'

	tpdir = safe_join(username, mapname)
	tpdir = safe_join(tpdir, thefolder)
	tpdir = safe_join(app.static_folder, tpdir)

	print '=== get_image()', username, mapname, timepoint, slice, channel
	print 'tpdir:', tpdir
	print 'thefile:', thefile
	
	return send_from_directory(tpdir, thefile, as_attachment=True, mimetype='image/tif')

##
# post
##

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
			filename = secure_filename(file.filename)

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
#
# old and testing
#
@app.route('/gettiff')
def gettiff():
    filename='data/rr30a/raw/rr30a_s0_ch2_0032.tif'
    #filename='img1.tif'
    file = 'rr30a_s0_ch2_0059.tif'
    return send_file(filename, mimetype='image/tif')
    #return send_from_directory('data/rr30a/raw', file

@app.route("/data")
def data():
    from cStringIO import StringIO
    
    import numpy as np

    myarray = np.ones([1024,1024]).astype('uint16')

    output = StringIO()
    np.savetxt(output, myarray)
    csv_string = output.getvalue()
    print csv_string
    return csv_string

@app.route("/plot")
def simple():
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


if __name__ == '__main__':
    #gettiff()
    # host= '0.0.0.0' will run on servers network ip
    app.run(host='0.0.0.0', port=5010)
    # this will run on localhost at port :5000
    #app.run(debug=True)

