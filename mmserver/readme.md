This is Python code to run a Flask server that provides a REST interface allowing Map Manager annotations and images to be retrieved.

Please see the main [PyMapManager][PyMapManager] documentation website.

For a full list of REST aPI endpoint, please see the full REST API [documentaiton][restapi]

Also see [mmio][mmio] to seemlesly load Map Manager annotations from the REST server using Python.

## Running the server

This will run the server locally at `http://localhost:5010`.

```
cd mmserver
python mmserver.py
```

The default Flask server that is used when running with `python mmserver.py` is **asynchronous**. This means that really fast or lots of user requests will get backed up and the server will not respond. To get around this, run a **synchronous** server with `gunicorn`.

Install gunicorn

	pip install gunicorn
	
On OSX (gunicorn requires sudo)

	cd mmserver
	sudo gunicorn -b 0.0.0.0:5010 mmserver:app

On Linux (no sudo needed)

	cd mmserver
	gunicorn -b 0.0.0.0:5010 mmserver:app
	
## Using the REST API in a scripting language

### In Python

```python
import json
import urllib2

url='http://localhost:5010/v2/public/rr30a/getmaptracing?mapsegment=&session=3&xstat=x&ystat=y&zstat=z'

mytracing = json.load(urllib2.urlopen("url"))

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

[1]: http://127.0.0.1:5010/public/rr30a/header
[2]: http://cudmore.duckdns.org
[mmio]: https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/mmio
[PyMapManager]: http://blog.cudmore.io/PyMapManager/
[restapi]: http://blog.cudmore.io/PyMapManager/rest-api/