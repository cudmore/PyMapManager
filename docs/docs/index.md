PyMapManager is a Python package to analyze time-series image stacks.

PyMapManager opens annotations created with the Igor Pro version of [Map Manager][1]. Allowing additional analysis to easily be performed.

There are three components to PyMapManager:

 - Python Package
 - Server
 - Desktop application
 
## PyMapManager Python package

See the [/examples][5] folder in the main GitHub repository for example Python code to easily perform additional analysis. Please also see the [API Documentation][2].

## PyMapManager server
 
The PyMapManager server allows web-based browsing of annotations and stacks. See [server documentation][3] for additional information.

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
[3]: https://github.com/cudmore/PyMapManager/tree/master/mmserver
[4]: https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/interface
[5]: https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/examples