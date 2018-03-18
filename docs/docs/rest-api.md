## Run the server

```
cd PyMapManager/app
python mmserver.py
```

This will run the server locally at `http://127.0.0.1:5000`

## Using the REST API in a program

### In Python

```python
import json
import urllib2

url='http://127.0.0.1:5000/v2/public/rr30a/getmaptracing?mapsegment=&session=3&xstat=x&ystat=y&zstat=z'

mytracing = json.load(urllib2.urlopen("url"))

# plot with matplotlib
import matplotlib.pyplot as plt
plt.plot(mytracing['x'],mytracing['y'])
```

### In Matlab

```matlab
url='http://127.0.0.1:5000/getmaximage/public/rr30a/0/2'
myimage = webread(url);
imshow(myimage)
```

## REST API

The following REST routes specify end-points that will return JSON text or images. 

We will be using the `public` user and the `rr30a` map included in the `mmserver/data/` folder.

The links on this page point to a development server that may or may not be running.

### Get help

[http://127.0.0.1:5000/help][/help]
	
### Get a list of maps

[http://127.0.0.1:5000/api/public/maps][/api/public/maps]
	
### Load a map

[api/v1/loadmap/public/rr30a][/loadmap/public/rr30a]
	
### Get annotation values

Here we will get an x-stat `days`, a y-stat `pDist`, and a z-stat `z` for map segment 0 across all sessions

[http://127.0.0.1:5000/v2/public/rr30a/getmapvalues?mapsegment=0&session=&xstat=days&ystat=pDist&zstat=z][getmapvalues]
	
	
### Get a tracing

Here we will get the x/y/z of a tracing (in um) for all map segments in session 3

[http://127.0.0.1:5000/v2/public/rr30a/getmaptracing?mapsegment=&session=3&xstat=x&ystat=y&zstat=z][gettracing]

### Get an image

Here we will get the 20th image in the stack for timepoint 3, channel 2

[http://127.0.0.1:5000/getimage/public/rr30a/3/2/20][getimage]
	
## Get a maximal intensity projection

Here we will get the maximal intensity projection of timepoint 0, channel 2

[http://127.0.0.1:5000/getmaximage/public/rr30a/0/2][getmax]
	


[/help]: http://cudmore.duckdns.org/help
[/api/public/maps]: http://cudmore.duckdns.org/api/v1/maplist/public
[/loadmap/public/rr30a]: http://cudmore.duckdns.org/api/v1/loadmap/public/rr30a
[getmapvalues]: http://cudmore.duckdns.org/api/v1/getmapvalues/public/rr30a?mapsegment=0&session=&xstat=days&ystat=pDist&zstat=z
[gettracing]: http://cudmore.duckdns.org/api/v1/getmaptracing/public/rr30a?mapsegment=&session=3&xstat=x&ystat=y&zstat=z
[getimage]:
[getimage]: http://cudmore.duckdns.org/api/v1/getimage/public/rr30a/3/2/20
[getmax]: http://cudmore.duckdns.org/api/v1/getmaximage/public/rr30a/0/2
