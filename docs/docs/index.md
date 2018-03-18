PyMapManager is a suite of Python tools to visualize, annotate, and analyze time-series image volumes. PyMapManager opens annotations created with the Igor Pro version of [Map Manager][1], allowing additional visualization and analysis to easily be performed.

There are three components to PyMapManager:

1. A Python package
2. A web server
3. A desktop application.

## 1) PyMapManager Python package

Install with

	pip install PyMapManager
	
To get started writing Python code to extend Map Manager analysis, see the iPython notebooks in the [/examples][5] folder. For more detailed install instructions, see [Install PyMapManager](install-pymapmanager). See the [API Documentation][2] for a full description of all the classes and functions.

## 2) PyMapManager server
 
The PyMapManager server provides a web-based front-end to browse Map Manager annotations and images. The PyMapManager server also provides a [REST API][6] to retrieve Map Manager annotations and images from within your favorite programming environment.

We have an [example server][client/server] to see this in action. Please note, this server is at an early development stage and might not always be available. 

### Browsing annotations

<IMG SRC="mmserver_purejs.png">

### Browsing annotations in time series stacks

<IMG SRC="mmserver_leaflet.png">
<IMG SRC="mmserver_leaflet2.png">
 
 
## 3) PyMapManager deskop application
 
**Development of this desktop application has been downgraded to focus on the PyMapManager web interface.**

The Qt version of PyMapManager is a desktop application. See [/PyQtMapManager][4]. 
 
<IMG SRC="pyMapManager_v2.png">
 
[1]: http://mapmanager.github.io
[2]: http://pymapmanager.readthedocs.io/en/latest/
[3]: install-client-server
[4]: https://github.com/cudmore/PyMapManager/tree/master/PyQtMapManager
[5]: https://github.com/cudmore/PyMapManager/tree/master/examples
[6]: rest-api
[client/server]: http://cudmore.duckdns.org