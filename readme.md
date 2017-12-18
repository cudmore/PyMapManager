
This is python code to load and visualize MapManager files. The workflow is to use <A HREF="http://blog.cudmore.io/mapmanager/">MapManager</A> to create annotated maps and stacks. Then, use PyMapManager to easily perform additional analysis.

This project will be merged with <A HREF="https://github.com/cmicek1/TiffViewer">PyQt TiffViewer</A> created by <A HREF="https://github.com/cmicek1">Chris Micek</A>.

## Python API interface

Python library to open and analyze Map Manager files.

Please see the <A HREF="http://blog.cudmore.io/PyMapManager">API Documentation</A>. We keep another copy at <A HREF="http://pymapmanager.readthedocs.io/en/latest/">API Documentation</A> and a third at <A HREF="http://robertcudmore.org/mapmanager/PyMapManager/docs/">here</A>.

See the <A HREF="https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/examples">PyMapManager/examples/</A> folder for ipython notebooks with code examples.

## Map Manager server

A server to browse and share Map Manager files via the web

<IMG SRC="images/mmserver_purejs.png" width=400>

This screenshot shows the web based browsing and plotting of Map Manager annotations.

## PyQt interface

The next generation desktop application version of Map Manager. Written in Python using PyQt interface and using backend PyMapManager as an engine.

A PyQt GUI interface is in <A HREF="https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/interface">/PyMapManager/interface</A>

<IMG SRC="images/pyMapManager_v2.png">

This screen shot shows the main interface window (left), a map plot (top center), a stack plot (top right), and a stack image plot (bottom right).


## Install Python PyMapManager package

Once installed, PyMapManager is available in python as `import pymapmanager`

 - Install [anaconda][1]
 - Install [tifffile][2]. This version is for Python 2.7, newer versions are for Python 3.x
 
    conda install -c conda-forge tifffile=0.12.1

 - Install PyMapManager
  
 	# cd into folder that contains `PyMapMAnager` folder
 	pip install -e PyMapManager


## Run the `mmserver` server

Once the serve is running, it is available at `http://0.0.0.0:5010/`

	cd mmserver
	python mmserver.py
	
   
## Install PyQt desktop application

 - For pyqt interface, Downgrade anaconda from PyQt5 to PyQt4
 
    conda uninstall pyqt
    conda install pyqt=4	
	  
## To do

 1. [done] Generate API documentation from doc strings
 2. [done] Load individual slices dynamically (how to query number of slices in .tif file?)
 2. [done] Use the mmserver REST API to make a standalone web-app using Flask, Angular, and Plotly

[1]: https://www.continuum.io/downloads
[2]: http://www.lfd.uci.edu/~gohlke/
