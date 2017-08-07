"""
A http server to serve mmMap files and images.
Server is run using Flask.
Implements a RESTful API.
"""

import os
import json
from datetime import datetime

from flask import Flask, make_response, send_file, send_from_directory, safe_join
from flask import jsonify

static_folder = '/Users/cudmore/Desktop/data'

#app = Flask(__name__, static_url_path='/data')
app = Flask(__name__, static_folder=static_folder)

@app.route('/')
def hello_world():
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
	
	if item == 'header':
		mapfile = mapname + '.txt'
	elif item == 'objmap':
		mapfile = mapname + '_objMap.txt'
	elif item == 'segmap':
		mapfile = mapname + '_segMap.txt'
	
	print '=== get_header()', username, mapname, item
	print 'mapdir:', mapdir
	print 'mapfile:', mapfile
	return send_from_directory(mapdir, mapfile)

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
	print tpdir
	print thefile
	
	return send_from_directory(tpdir, thefile, mimetype='image/tif')

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
    app.run(debug=True)

