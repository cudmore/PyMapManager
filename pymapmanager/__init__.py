from __future__ import absolute_import

"""
Prevent typing
    from pymapmanager.mmMap import mmMap
And instead type
    from pymapmanager import mmMap

I think the former will still work so does not break my existing code?
"""

from .mmMap import mmMap
from .mmStack import mmStack
from .mmStack import mmio
from .mmMapPlot2 import mmMapPlot2

"""
This will allow pymapmanager package to have a __version__ string
    import pymapmanager as pmm
    pmm.__version__
"""

from .version import __version__

