.. PyMapManager documentation master file, created by
   sphinx-quickstart on Fri Jan 12 20:55:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2

`PyMapManager <http://cudmore.github.io/PyMapManager>`_ is software to visualize and annotative 3D image time-series.

The PyMapManager package is available on `PyPi <https://pypi.python.org/pypi/pymapmanager>`_ and can be installed with::

	pip install PyMapManager

Classes
==================

* :py:class:`mmMap <pymapmanager.mmMap>` - A time-series of :py:class:`mmStack <pymapmanager.mmStack>`.
* :py:class:`mmStack <pymapmanager.mmStack>` - A 3D image volume, annotations, and :py:class:`mmStackLine <pymapmanager.mmStackLine>` tracings.
* :py:class:`mmStackLine <pymapmanager.mmStackLine>` - 3D tracings.

* :py:class:`mmMapPool <pymapmanager.mmMapPool>` - Pooling mmMap.
* :py:class:`mmStackPool <pymapmanager.mmStackPool>` - Pooling mmStack.

* :py:class:`mmMapPlot2 <pymapmanager.mmMapPlot2>` - Simplifies plotting annotations from a mmMap.

* :py:class:`mmio <pymapmanager.mmio>` - Interface to Map Manager server.

Examples
==================
* See the examples section on the main `documentation website <http://cudmore.github.io/PyMapManager/>`_.
* Also, see the `examples/ <https://github.com/cudmore/PyMapManager/tree/master/examples>`_ folder in main `GitHub repository <https://github.com/cudmore/PyMapManager>`_.

Links
==================
* PyMapManager `documentation website <http://cudmore.github.io/PyMapManager>`_.
* PyMapManager `GitHub repository <https://github.com/cudmore/PyMapManager>`_.
* Documentation for the `Igor Pro Version of MapManager <http://cudmore.github.io/mapmanager/>`_.
* Robert Cudmore's `homepage <http://robertcudmore.org>`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

