
PyMapManager is an ecosystem of tools to load and visualize time-series annotations and 3D image volumes.

The workflow is to use the Igor Pro version of <A HREF="http://blog.cudmore.io/mapmanager/">Map Manager</A> and then use PyMapManager to easily perform additional visualization and analysis.

Please see the main [PyMapManager](http://blog.cudmore.io/PyMapManager) documentation website.

## Repository contents

 - [pymapmanager/](pymapmanager/) : Python package to load and visualize time-series annotations and images.
 - [examples/](examples/) : Jupyter notebooks with example Python code using pymapmanager.
 - [mmserver/](mmserver/) : A Python Flask server that provides a REST interface to easily retrieve Map Manager annotations and images.
 - [mmclient/](mmclient/) : A user friendly front-end Javascript client to plot annotations and view image time-series from a `mmserver` REST server.
 - [pymapmanager/mmio.py](pymapmanager/mmio.py) : Helper class allowing pymapmanager Python code to load annotations and images from a [mmserver/](mmserver/) REST server.
 
## PyMapManager Python package

Python package to open and analyze Map Manager files. Please see the <A HREF="http://pymapmanager.readthedocs.io/en/latest/">API Documentation</A> and a backup copy <A HREF="http://robertcudmore.org/mapmanager/PyMapManager/docs/">here</A>. See the [examples/](examples/) folder for iPython notebooks with code examples.

## Map Manager server

A server to browse and share Map Manager annotates and time-series images via the web. The server uses the PyMapManager Python package as an back-end.

This screenshot shows web based browsing and plotting of Map Manager annotations.

<IMG SRC="docs/docs/img/mmserver_purejs.png" width=900>

These screenshots show web based browsing of 3D image volume time-series with spine annotations overlaid.

<IMG SRC="docs/docs/img/mmserver_leaflet.png" width=900>
<IMG SRC="docs/docs/img/mmserver_leaflet2.png" width=900>


## PyQt interface -- DEPRECIATED

The next generation desktop application version of Map Manager. Written in Python using the Qt interface library and using the PyMapManager Python package as an back-end.

This project will be merged with <A HREF="https://github.com/cmicek1/TiffViewer">PyQt TiffViewer</A> created by <A HREF="https://github.com/cmicek1">Chris Micek</A>.

The PyQt GUI interface is in [PyQtMapManager/](PyQtMapManager/)

<IMG SRC="docs/docs/img/pyMapManager_v2.png" width=800>

This screen shot shows the main PyQt interface window (left), a map plot (top center), a stack plot (top right), and a stack image plot (bottom right).


## Install the PyMapManager package

### Install from [PyPi](https://pypi.python.org/pypi/pymapmanager) using pip

	pip install PyMapManager

### install from download

Clone the repository

	git clone https://github.com/cudmore/PyMapManager.git

Install required Python libraries

	pip install -r PyMapManager/requirements.txt

Install PyMapManager package (from download)
  
	pip install PyMapManager/

Once installed, example maps can easily be loaded.

	from pymapmanager import mmMap
	path = 'PyMapManager/examples/exampleMaps/rr30a'
	myMap = mmMap(path)

See the [examples/](examples/) to get started.


## Run the Map Manager server

The server is made of two components, a back-end REST server and a client-side Javascript server.

 1. The back-end server is in `mmserver/mmserver.py` and provides a REST interface using Python Flask.
 2. The client-side Javascript server is in `mmclient/` and provides a front end point-and-click interface in a web browser.

### Run the back-end REST server

Install libraries

```
pip install -r PyMapManager/mmserver/requirements.txt
```

Run

```
cd PyMapManager/mmserver
python mmserver.py
```

Once running, the REST interface can be accessed via

```
http://localhost:5010
```

### Run the client-side Javascript server

This assumes [Node](https://nodejs.org/en/download/) has been manually downloaded and installed.

Install http-server

```
npm install http-server -g
```

Run

```
cd PyMapManager/mmclient
http-server
```

Once running, the client-side server can be accessed via

```
http://localhost:8080
```
	
   
## Run the PyQt interface -- DEPRECIATED

We have downgraded development of the PyQt interface to focus on the web client/server version of Map Manager

### Downgrade anaconda from PyQt5 to PyQt4
 
```
conda uninstall pyqt
conda install pyqt=4	
```

### Run the qt interface

```
cd PyMapManager/interface
python main.py
```
	  
 
