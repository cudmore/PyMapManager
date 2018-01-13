from __future__ import absolute_import
'''
Prevent typing
    from pymapmanager.mmMap import mmMap
And instead type
    from pymapmanager import mmMap

I think the latter will still work so does not break my existing code?

'''

# this will allow
#    import pymapmanager as pmm
#    pmm.__version__

from .version import __version__

from .mmMap import mmMap
from .mmStack import mmStack
