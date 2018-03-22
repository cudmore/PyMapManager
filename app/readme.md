This is Python code to run a web server which will create a point-and-click interface to browse Map Manager annotations and image time-series. The server also includes a REST interface allowing data to be retreived from your favorite programming environment.

Please see the main [PyMapManager](http://blog.cudmore.io/PyMapManager) documentation website and examples of [REST API endpoints](http://blog.cudmore.io/PyMapManager/rest-api/).

## Installation

Make a directory to work in

	mkdir mmInstall
	cd mmInstall
	
Clone the PyMapManager repository

	git clone --depth=1 https://github.com/cudmore/PyMapManager.git

Clone the PyMapManager-Data repository

	git clone --depth=1 https://github.com/mapmanager/PyMapManager-Data.git

Make a Python virtual environment

	virtualenv venv
	source venv/bin/activate

Install PyMapManager

	pip install --no-cache-dir PyMapManager/

Install additional requirements for server

	pip install --no-cache-dir -r PyMapManager/app/requirements.txt
	
## Running the server

```
cd PyMapManager/app
python mmserver.py
```

This will run the server locally at `http://localhost:5000`. Have fun browsing.

## Running a production level server

Running the server with `python mmserver.py` is a good way to get started quickly. Yet, this is a very simplified example. In reality, the server should be run **synchronously** using either gunicorn or uwsgi and then served through a proper web-server such as Apache or nginx. We provide an easy to use Docker container to do exactly this! See [install server](http://blog.cudmore.io/PyMapManager/install-server/) for more information.


## Using the REST API in a scripting language

Once the server is running, annotations and images can be queried via the [REST](http://blog.cudmore.io/PyMapManager/rest-api/) interface.

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

