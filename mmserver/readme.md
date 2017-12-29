This is python code to run a Flask server that provides a REST interface allowing Map Manager annotations and images to be retrieved.

Please see the PyMapManager [REST API][restapi] documentation for details.

Also see [mmio][3] to seemlesly load Map Manager annotations from the REST server using Python.

## Running the server

This will run the server locally at `http://127.0.0.1:5010`.

```
cd mmserver
python mmserver.py
```

## Using the REST API in a program

### In Python

```python
import json
import urllib2

url='http://127.0.0.1:5010/v2/public/rr30a/getmaptracing?mapsegment=&session=3&xstat=x&ystat=y&zstat=z'

mytracing = json.load(urllib2.urlopen("url"))

# plot with matplotlib
import matplotlib.pyplot as plt
plt.plot(mytracing['x'],mytracing['y'])
```

### In Matlab

```matlab
url='http://127.0.0.1:5010/getmaximage/public/rr30a/0/2'
myimage = webread(url);
imshow(myimage)
```

[1]: http://127.0.0.1:5010/public/rr30a/header
[2]: http://cudmore.duckdns.org
[3]: https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/mmio
[PyMapManager]: http://blog.cudmore.io/PyMapManager/
[restapi]: http://blog.cudmore.io/PyMapManager/rest-api/