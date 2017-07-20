
This is python code to load and visualize MapManager files. The workflow is to use <A HREF="http://blog.cudmore.io/mapmanager/">MapManager</A> to create maps and stacks. Then, use PyMapManager to easily perform additional analysis.

This project will be merged with <A HREF="https://github.com/cmicek1/TiffViewer">PyQt TiffViewer</A> created by <A HREF="https://github.com/cmicek1">Chris Micek</A>.

## API interface

Please see the <A HREF="http://pymapmanager.readthedocs.io/en/latest/">API Documentation</A>. We have a second copy <A HREF="http://robertcudmore.org/mapmanager/PyMapManager/docs/">here</A>.

See the <A HREF="https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/examples">PyMapManager/examples/</A> folder for ipython notebooks with code examples.

## PyQt interface

A PyQt GUI interface is in <A HREF="https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/interface">/PyMapManager/interface</A>

## PyQt interface examples

<IMG SRC="images/pyMapManager_v2.png">

This screen shot shows the main interface window (left), a map plot (top center), a stack plot (top right), and a stack image plot (bottom right).

## Install

 - Install anaconda: https://www.continuum.io/downloads
 - Install tifffile: http://www.lfd.uci.edu/~gohlke/
 
    conda install -c conda-forge tifffile=0.12.1

 - Downgrade anaconda from PyQt5 to PyQt4
 
    conda uninstall pyqt
    conda install pyqt=4
     
## To do

 1. Generate API documentation from doc strings
 2. Load individual slices dynamically (how to query number of slices in .tif file?)
 2. Use the API to make a standalone web-app using Bokeh

