This is Python code to run a web server which will create a point-and-click interface to Map Manager annotations and image time-series. The server also includes a REST interface allowing data to be retreived from your favorite programming environment.

Please see the main [PyMapManager](http://blog.cudmore.io/PyMapManager) documentation website and examples of [REST API endpoints](http://blog.cudmore.io/PyMapManager/rest-api/).

## Installation

Make a directory to work in

	mkdir mmInstall
	cd mmInstall
	
Clone the PyMapManager repository

	git clone https://github.com/cudmore/PyMapManager.git

Clone the PyMapManager-Data repository

	git clone https://github.com/mapmanager/PyMapManager-Data.git

Make a Python virtual environment

	virtualenv venv
	source venv/bin/activate

Install PyMapManager

	pip install --no-cache-dir PyMapManager/

Install additional requirements for server

	pip install --no-cache-dir -r PyMapManager/app/requirements.txt
	
## Running the server

You need a redis-server running. Install it on OSX with `brew install redis-server` or on most variants of Linux with `sudo apt-get install redis-server`. See [redis](http:///redis.io) homepage for more info.

	redis-server
	
This will run the server locally at `http://localhost:5000`.

```
cd PyMapManager/app
python mmserver.py
```

Please note, this is a very simplified example. In reality, the REST server should be run **synchronously** using either gunicorn or uwsgi and then served through a proper web-server such as Apache or nginx.


## Using the REST API in a scripting language

### In Javascript

NEED TO ADD CODE EXAMPLES

### In Python

Map Manager maps can easily be loaded from the server, just like they are loaded from a local file

```python
from pymapmanager import mmMap
urlmap='rr30a' # map 'rr30a' is an example map in PyMapMAnager/exmples/exampleMaps
mymap = mmMap(urlmap=urlmap)
```

Or the server can be addressed directly

```python
import json
import urllib2

# grab the tracing (from the server)
url='http://localhost:5000/api/v1/getmaptracing/public/rr30a?mapsegment=&session=3&xstat=x&ystat=y&zstat=z'
mytracing = json.load(urllib2.urlopen(url))

# plot with matplotlib
import matplotlib.pyplot as plt
plt.plot(mytracing['x'],mytracing['y'])
```



### In Matlab

```matlab
url='http://localhost:5000/getmaximage/public/rr30a/0/2'
myimage = webread(url);
imshow(myimage)
```

