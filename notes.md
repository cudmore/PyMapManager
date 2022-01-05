## Development notes

### 20180319

1) Problems with installing and running in a virtual environment. Get the error:

	RuntimeError: Python is not installed as a framework. The Mac OS X backend will not be able to fun
	
mmserver.py needs this BEFORE importing any matplotlib

	import matplotlib
	matplotlib.use('TkAgg')

2) need to remove plot import from __init__.py

3) write out and test full virtual env install, missing flask for example !!!

### Using fresh install of Anaconda on OSX

    # downgrade qt5 to qt4
    conda uninstall pyqt
    conda install pyqt=4

    # we still need to get correct version of matplotlib
    # stock install of anaconda on work osx does not have matplotlib
    conda install -c conda-forge matplotlib=2.0.2
    conda install -c conda-forge tifffile=0.12.1

    # install PyMapMAnager
    pip install -e Dropbox/PyMapManager

### Install

Main archive folder has caps `PyMapManager`, this contains:

 - `setup.py` file
 - folder of `pymapmanager` code
 - auto generated `docs` folder

Code folder inside of PyMapManager is lower-case `pymapmanager`, at same level as setup.py and contians all the code

In this way `pip install -e Dropbox/PyMapManager` can then be used in python with `import pymapmanager`

Dropbox is NOT case sensitive, when I change case of enclosing `pymapmanager` folder it DOES NOT sync.

	cd
	pip install -e Dropbox/PyMapManager
	

### spreadsheet for pandas in qt

    https://github.com/draperjames/qtpandas

    pip install qtpandas

### Sphinx

    sphinx-quickstart
    
sphinx readthedocs theme

    pip install sphinx_rtd_theme

Make sure config.py has
    
    from mock import MagicMock
    
    class Mock(MagicMock):
        @classmethod
        def __getattr__(cls, name):
            return MagicMock()
    
    MOCK_MODULES = ['pygtk', 'gtk', 'gobject', 'argparse', 'numpy', 'pandas','sip', 'PyQt4', 'PyQt4.QtGui', 'tifffile']
    sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)
    
    import os
    import sys
    sys.path.insert(0, os.path.abspath('../..'))

    html_theme = "sphinx_rtd_theme"

    # remove duplicate modile name in every constructor
    # e.g. mmMap.mmMap()
    add_module_names = False

    # exlude directories from build, in particular 'old'
    exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'old']

rebuild docs

    sphinx-apidoc -o . ..
    make html

### Sphinx (Again)

Trying to use Sphinx napolean: http://www.sphinx-doc.org/en/stable/ext/napoleon.html

Tweek `docs/source/conf.py`

    exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'old', 'pdoc']

    extensions = ['sphinx.ext.autodoc',
        'sphinx.ext.viewcode',
        'sphinx.ext.githubpages',
        'sphinx.ext.napoleon']

    html_theme = "sphinx_rtd_theme"

To build the docs

    cd ~/Dropbox/PyMapManager/pymapmanager/docs/
    sphinx-apidoc -f -o docs ~/Dropbox/PyMapManager
    make html

This should put output into root /docs/ folder (holding index.html) and github /docs/ option should work?

    cd ~/Dropbox/PyMapManager/pymapmanager/docs/ #this has source directory with .rst files
    
    # if i add a module i need to do this
    sphinx-apidoc -f -o source ~/Dropbox/PyMapManager
    # or
    sphinx-apidoc -fe -o source ~/Dropbox/PyMapManager
    
    # generic rebuild (do this all the time)
    sphinx-build -b html source/ ../../docs
    
### Github

Remove all references to .git

    find . -name .git -print0 | xargs -0 rm -rf
    
### mkdocs 20171129

`PyMapManager/docs` now has mkdocs website

`PyMapManager/docs/api` now has Sphinx API documentation

Push new Sphinx api with

	sphinx-build -b html source/ ../../docs/api
	
Make new mkdocs with

	cd ~/Dropbox/PyMapManager
	mkdocs new docs
	
Push to mkdocs to github with

	# need to do this in github repo, NOT Dropbox repo !!!
	cd ~/Sites/PyMapManager/docs
	mkdocs gh-deploy --clean

Make sure github repo is using gh-branch for docs

### pdoc

Download forked git repo from https://github.com/j6k4m8/pdoc

    # I am updating this code to tweek interface
    # use pip install -e' and changes in code will propogate to python
    pip install -e ~/Downloads/pdoc-master

    #then this command works
    pdoc PyMApManager --html --html-dir="docs" --overwrite --docstring-style=google
    
    # then from package folder '/Users/cudmore/Dropbox/PyMapManager'
    pdoc PyMapManager --html --html-dir="docs" --overwrite --docstring-style=google
    
    #removed generation of mro by modifying html.maco 
    % if 0 and len(mro) > 0:

Tweeked html.maco to hide __init__

        % if len(methods) > 0:
          <h3>Methods</h3>
          % for f in methods:
            % if f.name != "__init__":            	
              ${show_func(f)}
            % endif
          % endfor
        % endif

Changed __init__.py in module to strip out inherited class members/functions.
 See: https://github.com/BurntSushi/pdoc/issues/15

		# abb ADDED
		# Only include attributes in this module or class, not inherited attributes
        cls_dict_names = self.cls.__dict__.keys()
        def is_in_dict(n):
            return n in cls_dict_names
        # /ADDED

        #return dict([(n, o) for n, o in idents.items() if exported(n)])
        return dict([(n, o) for n, o in idents.items() if exported(n) and is_in_dict(n)]) # abb MODIFIED

Added a link back to index.html in html.mako

    #changed this
    <div id="sidebar">
      <h1>Index</h1>

    #to this
    <div id="sidebar">
      <h1><A HREF="index.html">Index</A></h1>

To generate pdoc
    cd /Users/cudmore/Dropbox/
    pip install -e PyMapManager
    cd PyMapManager
    pdoc PyMapManager --html --html-dir="docs" --overwrite --docstring-style="google"
    
    # SHOULD make /doc/PyMapManager/ inside PyMapManager MODULE (not first level which is PACKAGE
    
- check in in onpick() does it respect nan?

## Downloaing data from BIL

One of my datasets is here and includes raw images and folders of txt files with annotations

```
https://download.brainimagelibrary.org/d9/01/d901fb2108458eca/rr30a/
```

```
line/                                              04-Jan-2018 09:19                   -
max/                                               02-Oct-2015 14:18                   -
stackdb/                                           04-Jan-2018 09:03                   -
rr30a_s0_ch1.tif                                   02-Oct-2015 14:30           146883164
rr30a_s0_ch2.tif                                   02-Oct-2015 14:30           146883164
rr30a_s1_ch1.tif                                   02-Oct-2015 14:30           136391514
rr30a_s1_ch2.tif                                   02-Oct-2015 14:30           136391514
rr30a_s2_ch1.tif                                   02-Oct-2015 14:30           146883164
rr30a_s2_ch2.tif                                   02-Oct-2015 14:30           146883164
rr30a_s3_ch1.tif                                   02-Oct-2015 14:30           146883164
rr30a_s3_ch2.tif                                   02-Oct-2015 14:30           146883164
rr30a_s4_ch1.tif                                   02-Oct-2015 14:30           146883164
rr30a_s4_ch2.tif                                   02-Oct-2015 14:30           146883164
rr30a_s5_ch1.tif                                   02-Oct-2015 14:30           167866464
rr30a_s5_ch2.tif                                   02-Oct-2015 14:30           167866464
rr30a_s6_ch1.tif                                   02-Oct-2015 14:30           146883164
rr30a_s6_ch2.tif                                   02-Oct-2015 14:30           146883164
rr30a_s7_ch1.tif                                   02-Oct-2015 14:30           167866464
rr30a_s7_ch2.tif                                   02-Oct-2015 14:30           167866464
rr30a_s8_ch1.tif                                   02-Oct-2015 14:30           146883164
rr30a_s8_ch2.tif                                   02-Oct-2015 14:30           146883164
rr30a_s9_ch1.tif                                   28-Apr-2016 18:37            25710592
rr30a_s9_ch2.tif                                   28-Apr-2016 18:37            25710592
```