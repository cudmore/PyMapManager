
PyMapManager is Python package to load and visualize time-series annotations created in Map Manager. The workflow is to use the Igor Pro version of <A HREF="http://blog.cudmore.io/mapmanager/">Map Manager</A> to create annotated time-series. Then, use the PyMapManager Python package to easily perform additional visualization and analysis.

Please see the main [PyMapManager][PyMapManager] documentation website.

## PyMapManager Python package

Python package to open and analyze Map Manager files. Please see the <A HREF="http://pymapmanager.readthedocs.io/en/latest/">API Documentation</A> and a backup copy <A HREF="http://robertcudmore.org/mapmanager/PyMapManager/docs/">here</A>. See the <A HREF="https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/examples">PyMapManager/examples/</A> folder for iPython notebooks with code examples.

## Map Manager server

A server to browse and share Map Manager annotates and time-series images via the web. The server uses the PyMapManager Python package as an back-end.

This screenshot shows web based browsing and plotting of Map Manager annotations.

<IMG SRC="images/mmserver_purejs.png" width=900>

These screenshots show web based browsing of 3D image volume time-series with spine annotations overlaid.

<IMG SRC="images/mmserver_leaflet.png" width=900>
<IMG SRC="images/mmserver_leaflet2.png" width=900>


## PyQt interface

The next generation desktop application version of Map Manager. Written in Python using the Qt interface library and using the PyMapManager Python package as an back-end.

This project will be merged with <A HREF="https://github.com/cmicek1/TiffViewer">PyQt TiffViewer</A> created by <A HREF="https://github.com/cmicek1">Chris Micek</A>.

The PyQt GUI interface is in <A HREF="https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/interface">/PyMapManager/interface</A>

<IMG SRC="images/pyMapManager_v2.png" width=800>

This screen shot shows the main PyQt interface window (left), a map plot (top center), a stack plot (top right), and a stack image plot (bottom right).


## Install Python PyMapManager package

Once installed, PyMapManager is available in python as `import pymapmanager`

 - Install [anaconda][1]
 - Install [tifffile][2]. This version is for Python 2.7, newer versions are for Python 3.x

```
conda install -c conda-forge tifffile=0.12.1
```

 - Install PyMapManager
  
```
pip install -e PyMapManager
```

## Run the Map Manager server

The server is made of two components, a back-end server and a client-side javascript server.

 1. The back-end server is in `mmserver/mmserver.py` and provides a REST interface using Python Flask
 2. The client-side javascript server is in `mmclient/index.html` and provides a front end gui that can be browsed with a web browser.

### Run the back-end Python Flask REST api

```
cd mmserver
python mmserver.py
```

Once running, the REST interface can be accessed via

```
http://127.0.0.1:5010
```

### Run the client-side javascript server

```
cd mmclient
http-server
```

Once running, the client-side server can be accessed via

```
http://127.0.0.1:8080
```
	
   
## Run the PyQt interface

We have ceased development of the PyQt interface to focus on the web client/server version of Map Manager

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
	  
 
[1]: https://www.continuum.io/downloads
[2]: http://www.lfd.uci.edu/~gohlke/
[PyMapManager]: http://blog.cudmore.io/PyMapManager/

