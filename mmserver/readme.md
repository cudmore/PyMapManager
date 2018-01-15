This is Python code to run a Flask server that provides a REST interface allowing Map Manager annotations and images to be retrieved.

Please see the main [PyMapManager](http://blog.cudmore.io/PyMapManager) documentation website.

This REST server is accessed by the Javascript client in [mmclient](https://github.com/cudmore/PyMapManager/tree/master/mmclient).

See the full list of [REST API endpoints](http://blog.cudmore.io/PyMapManager/rest-api/).

## Installation

Clone the main PyMapManager repository

	git clone https://github.com/cudmore/PyMapManager.git

Make a Python virtual environment in `PyMapManager/mmserver`

	cd PyMapManager/mmserver
	virtualenv venv
	source venv/bin/activate

Install the required Python libraries

	pip install -r requirements.txt

Other than that, there is no formal installation. This is a stand-alone Python script, not a Python Package.
	
## Running the server

This will run the server locally at `http://localhost:5010`.

```
cd PyMapManager/mmserver
python mmserver.py
```

Please note, this is a very simplified example. In reality, the REST server should be run **synchronously** using either gunicorn or uwsgi and then served through a proper web-server such as Apache or nginx.


## Using the REST API in a scripting language

### In Javascript

See the [mmclient](https://github.com/cudmore/PyMapManager/tree/master/mmclient).

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
url='http://localhost:5010/api/v1/getmaptracing/public/rr30a?mapsegment=&session=3&xstat=x&ystat=y&zstat=z'
mytracing = json.load(urllib2.urlopen(url))

# plot with matplotlib
import matplotlib.pyplot as plt
plt.plot(mytracing['x'],mytracing['y'])
```



### In Matlab

```matlab
url='http://localhost:5010/getmaximage/public/rr30a/0/2'
myimage = webread(url);
imshow(myimage)
```

