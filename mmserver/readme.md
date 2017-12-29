Please see the main [PyMapManager][PyMapManager] documentation website.

## Contents

### 1) Python code to run a REST interface with Python Flask.

    mmserver/mmserver.py
    
### 2) Client side interface to browse maps on the server

```
mmclient/index.html
mmclient/static/mmserver.js
mmclient/static/mmserver.css
```
	
## See [mmio][3] to seemlesly load Map Manager annotations from the REST server using Python.

## Running the server

```
cd mmserver
python mmserver.py
```

## Rest interface

#### Load a map

	http://127.0.0.1:5010/loadmap/public/rr30a
	
#### Get values for session 1

	http://127.0.0.1:5010/getmapvalues?session=1&xstat=x&ystat=y&zstat=z
	
#### Get Map Header

    [http://127.0.0.1:5010/public/rr30a/header][1]

#### Get 3D object map

    http://127.0.0.1:5010/public/rr30a/objmap

#### Get 3D segment map

    http://127.0.0.1:5010/public/rr30a/segmap


#### Get timepoint 1 stack db

    http://127.0.0.1:5010/public/rr30a/1/stackdb

#### Get timepoint 1, intensity for channel 2

    http://127.0.0.1:5010/public/rr30a/1/int/2

#### Get timepoint 1 segment tracing

    http://127.0.0.1:5010/public/rr30a/1/line

#### Get timepoint 1 image, slice 10, channel 2 (for now, this downloads the whole stack)

    http://127.0.0.1:5010/public/rr30a/1/image/10/2

#### get a zip file of the map (now raw data included)

    http://127.0.0.1:5010/public/rr30a/zip         

[1]: http://127.0.0.1:5010/public/rr30a/header
[2]: http://cudmore.duckdns.org
[3]: https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/mmio
[PyMapManager]: http://blog.cudmore.io/PyMapManager/