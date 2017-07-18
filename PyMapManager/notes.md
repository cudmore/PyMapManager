## Development notes

### Using fresh install of Anaconda on OSX

    # work osx is 10.10.1 Yosemite
    # home osx is

    # downgrade qt5 to qt4
    conda uninstall pyqt
    conda install pyqt=4

    # we still need to get correct version of matplotlib
    # stock install of anaconda on work osx does not have matplotlib
    conda install -c conda-forge matplotlib=2.0.2
    conda install -c conda-forge tifffile=0.12.1

    # install PyMapMAnager
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

Tweek conf.py

    exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'old', 'pdoc']

    extensions = ['sphinx.ext.autodoc',
        'sphinx.ext.viewcode',
        'sphinx.ext.githubpages',
        'sphinx.ext.napoleon']

    html_theme = "sphinx_rtd_theme"

To build the docs

    cd ~/Dropbox/PyMapManager/PyMapManager/docs/
    sphinx-apidoc -f -o docs ~/Dropbox/PyMapManager
    make html
    
### Github

Remove all references to .git

    find . -name .git -print0 | xargs -0 rm -rf
    
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