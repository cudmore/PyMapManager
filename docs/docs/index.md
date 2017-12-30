PyMapManager is a suite of Python tools to analyze time-series image stacks.

PyMapManager opens annotations created with the Igor Pro version of [Map Manager][1]. Allowing additional visualization and analysis to easily be performed.

There are three components to PyMapManager: a Python package, a data client/server, and a desktop application.

## PyMapManager Python package

To get started writing Python code to interface with Map Manager analysis, see the iPython notebooks in [/examples][5].

For full class documentation, see the [API Documentation][2].

## PyMapManager client/server
 
The PyMapManager server provides a web based [REST API][6] to retrieve Map Manager annotations and images.

The PyMapManager client provides a web-based front-end to browse annotations and images off the server.

We have an [example client/server][client/server] to see this in action.

### Browsing annotations

<IMG SRC="mmserver_purejs.png">

### Browsing annotations in time series stacks

<IMG SRC="mmserver_leaflet.png">
<IMG SRC="mmserver_leaflet2.png">
 
 
## PyMapManager deskop application
 
The Qt version of PyMapManager is a desktop application. See [github repository][4].
 
<IMG SRC="pyMapManager_v2.png">
 
[1]: http://blog.cudmore.io/mapmanager
[2]: http://pymapmanager.readthedocs.io/en/latest/
[3]: install-client-server
[4]: https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/interface
[5]: https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/examples
[6]: rest-api
[client/server]: http://robertcudmore.org/mmclient